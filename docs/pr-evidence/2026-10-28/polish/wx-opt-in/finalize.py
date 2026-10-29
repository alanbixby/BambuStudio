#!/usr/bin/env python3
"""Record read-only integration context and hash the completed scratch handoff."""
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
APP_SHA = '0b34fcad456618e5d023e4f475dffb3f75ae6472'
WX_SHA = '3fea0af433d9630f79eaf8fbfc062364ba456be3'
APP_REPO = '/home/bxb/.t3-nightly/projects/bambu-studio-upstream'
WX_REPO = '/home/bxb/.t3-nightly/projects/bambu-wx-upstream'
context = []
for args in [
    ['git', '-C', APP_REPO, 'show', APP_SHA + ':deps/wxWidgets/wxWidgets.cmake'],
    ['git', '-C', WX_REPO, 'diff', 'e2fa9bda52f720242e35def30ac4a01fbe75f5a8',
     'abb542694ef4534a50e65c5b877b2774d02952ae', '--', 'src/gtk/window.cpp',
     'src/gtk/control.cpp', 'include/wx/window.h', 'interface/wx/window.h',
     'interface/wx/sysopt.h'],
]:
    proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    context.append({'argv': args, 'exit_code': proc.returncode,
                    'stdout': proc.stdout, 'stderr': proc.stderr})
assert context[1]['stdout'] == ''
recipe = context[0]['stdout'].splitlines()
assert recipe[26].strip() == 'GIT_REPOSITORY "https://github.com/bambulab/wxWidgets"'
assert recipe[27].strip() == 'GIT_TAG master'
(OUT / 'integration-context.json').write_text(json.dumps(context, indent=2) + '\n')

source_manifest = []
for tree in ['original', 'candidate']:
    for file in sorted((OUT / tree).rglob('*')):
        if not file.is_file():
            continue
        data = file.read_bytes()
        project = file.relative_to(OUT / tree).parts[0]
        source_manifest.append({
            'artifact': str(file.relative_to(OUT)),
            'base_sha': WX_SHA if project == 'wx' else APP_SHA,
            'sha256': hashlib.sha256(data).hexdigest(),
            'git_blob_sha1': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(),
            'bytes': len(data),
        })
(OUT / 'source-manifest.json').write_text(json.dumps(source_manifest, indent=2) + '\n')

findings = {
    'task': 'Scratch implementation of default-off wxGTK3 font-DPI opt-in',
    'implementation_status': 'candidate_complete_unapplied',
    'reviewed_exact_heads': {'wx': WX_SHA, 'app': APP_SHA},
    'additional_exact_bases_checked': {
        'wx_frozen_upstream': 'e2fa9bda52f720242e35def30ac4a01fbe75f5a8',
        'wx_current_upstream': 'abb542694ef4534a50e65c5b877b2774d02952ae',
    },
    'new_findings_count': 0,
    'open_candidate_blocking_count': 0,
    'open_parent_integration_blocking_count': 1,
    'open_blocking_count': 1,
    'count_scope': 'The one open blocker is inherited WXSOL-001, owned by the parent integration; no candidate seam blocker was found.',
    'findings': [{
        'id': 'WXSOL-001',
        'severity': 'blocking',
        'status': 'partially_addressed_by_unapplied_candidate_pending_parent_integration',
        'novelty': 'Inherited verified finding, not a new candidate defect.',
        'title': 'The compatibility gate is supplied, but the app still floats its wx dependency',
        'locations': [
            {'sha': APP_SHA, 'path': 'deps/wxWidgets/wxWidgets.cmake', 'line': 27},
            {'sha': APP_SHA, 'path': 'deps/wxWidgets/wxWidgets.cmake', 'line': 28},
            {'sha': WX_SHA, 'path': 'src/gtk/window.cpp', 'line': 4391,
             'candidate': 'wx-opt-in.patch adds the default-off guard at candidate line 4394'},
        ],
        'trigger': 'Integrating only the app SetOption, without selecting an exact wx revision containing the gate and both GTK fixes, leaves dependency selection on upstream master.',
        'outcome': 'The selected dependency is not established by these scratch patches. The opt-in fixes the old-consumer policy only after the wx candidate is actually integrated; source/runtime integration remains unverified.',
        'smallest_practical_fix': 'Parent integrates this small wx gate on the intended wx base, then pins its exact reachable SHA and correct repository URL in a separate app integration PR stacked on corrected consumers. No old release branch edits are required by this default-off mechanism.',
        'verification_needed': 'Parent verifies final diff, exact wx ancestry/blobs and declared-repository reachability, then rebuilds wx and Bambu together and checks opted and unopted consumers at GTK3 font DPI 96/144 and GDK scale 1/2. Obtain native OS evidence before any all-OS claims.',
        'blocking_scope': 'Completing/claiming the reproducible integration; does not mean a flaw was found in the delivered default-off candidate.',
        'evidence': ['integration-context.json', 'verification.json', 'test-commands.json',
                     'wx-opt-in.patch', 'app-opt-in.patch'],
    }],
    'checks': {
        'options_on_probe_assertions': 4582484,
        'options_off_probe_assertions': 271184,
        'red_control_exit': 1,
        'expected_success_commands': 'All exit 0; see test-commands.json',
        'native_gui_or_project_build': False,
    },
    'limitations': [
        'Extracted conversion/wrapper/rounding code and actual sysopt header, with GTK/window/value-object doubles; not a complete wx or Bambu compilation.',
        'Enabled wxSystemOptions lookup is a double; actual string/environment semantics were inspected in frozen source only.',
        'Windows/macOS/GTK2 startup checks are Linux-host macro probes, not native OS builds or runtime tests.',
        'Startup ordering combines source call-site inspection and a simulated inner routine; it is not an exhaustive pre-OnInit runtime trace.',
        'No native GTK rendering, full options-disabled build, shared-library/ABI check or merge-readiness approval.',
        'No source repository/index/ref/application/GUI/profile/printer changes, project builds, delegation or publication.',
    ],
}
(OUT / 'findings.json').write_text(json.dumps(findings, indent=2) + '\n')

manifest = []
for file in sorted(OUT.rglob('*')):
    if file.is_file() and file.name != 'artifact-hashes.sha256':
        manifest.append(hashlib.sha256(file.read_bytes()).hexdigest() + '  ' + str(file.relative_to(OUT)))
(OUT / 'artifact-hashes.sha256').write_text('\n'.join(manifest) + '\n')
print('Recorded {} artifact hashes; candidate blockers 0; inherited parent integration blocker 1.'.format(len(manifest)))
