#!/usr/bin/env python3
"""Focused extraction/stub probes, not a wx/Bambu build or native GUI test."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

OUT = Path(__file__).resolve().parent
TMP = OUT / 'tmp'
TMP.mkdir(exist_ok=True)
BUILD = OUT / 'probes'
(BUILD / 'include' / 'wx').mkdir(parents=True, exist_ok=True)
ENV = dict(os.environ, TMPDIR=str(TMP), TMP=str(TMP), TEMP=str(TMP),
           CCACHE_DISABLE='1', PYTHONDONTWRITEBYTECODE='1')
commands = []
results = {}

def run(argv, expected=0, cwd=OUT):
    proc = subprocess.run(list(map(str, argv)), cwd=cwd, env=ENV,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    record = {'argv': list(map(str, argv)), 'cwd': str(cwd), 'exit_code': proc.returncode,
              'expected_exit_code': expected, 'stdout': proc.stdout, 'stderr': proc.stderr}
    commands.append(record)
    (OUT / 'test-commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    assert proc.returncode == expected, record
    return record

def original(project, path):
    return (OUT / 'original' / project / path).read_text()

def candidate(project, path):
    return (OUT / 'candidate' / project / path).read_text()

def between(text, start, end):
    return text[text.index(start):text.index(end, text.index(start))]

wx_old = original('wx', 'src/gtk/window.cpp')
wx_new = candidate('wx', 'src/gtk/window.cpp')
old_block = between(wx_old, '#ifdef __WXGTK3__\n\n// ---', '#endif // __WXGTK3__') + '#endif // __WXGTK3__\n'
new_block = between(wx_new, '#ifdef __WXGTK3__\n\n// ---', '#endif // __WXGTK3__') + '#endif // __WXGTK3__\n'
guard = ('    // Keep legacy applications on identity conversions unless they opt in.\n'
         '    if ( wxSystemOptions::GetOptionInt("gtk.window.font-dpi-scaling") != 1 )\n'
         '        return 1;\n\n')
assert wx_new.count(guard) == 1
assert wx_new.replace(guard, '') == wx_old
assert new_block.replace(guard, '') == old_block
assert new_block.index('GetOptionInt') < new_block.index('window->GetHandle()')
assert 'static double' not in new_block
assert 'include/wx/window.h' not in (OUT / 'wx-opt-in.patch').read_text()
results['wx_scope'] = 'Only the early four-line guard changes executable wx source; no scale cache, includes/API/Windows/macOS/GTK2/wx1 changes.'

wrappers = between(original('wx', 'include/wx/window.h'),
                   '    static wxSize FromDIP(', '\n\n\n        // Dialog units')
rounding = between(original('wx', 'include/wx/math.h'),
                   'inline int wxRound(double x)', 'inline int wxRound(float x)')
header = original('wx', 'include/wx/sysopt.h')
(BUILD / 'include' / 'wx' / 'sysopt.h').write_text(header)
(BUILD / 'include' / 'wx' / 'object.h').write_text('''#ifndef PROBE_OBJECT_H
#define PROBE_OBJECT_H
#include <string>
class wxObject {};
class wxString {
public:
    std::string text;
    wxString(const char* value = "") : text(value) {}
};
const wxString wxEmptyString;
#define WXDLLIMPEXP_BASE
#define WXUNUSED(name)
#endif
''')
probe = (OUT / 'probe_body.inc').read_text()
for key, value in [('@WRAPPERS@', wrappers), ('@ROUND@', rounding),
                   ('@BASELINE@', old_block), ('@CANDIDATE@', new_block)]:
    probe = probe.replace(key, value)
assert '@' not in probe
(BUILD / 'conversion.cpp').write_text(probe)
flags = ['g++', '-std=c++98', '-pedantic-errors', '-Wall', '-Wextra', '-Werror',
         '-O0', '-g', '-fsanitize=undefined', '-fno-sanitize-recover=all',
         '-I' + str(BUILD / 'include')]
run(['g++', '--version'])
for options in [1, 0]:
    executable = BUILD / ('conversion-options-' + str(options))
    run(flags + ['-D__WXGTK3__', '-DwxUSE_SYSTEM_OPTIONS=' + str(options),
                 BUILD / 'conversion.cpp', '-o', executable])
    result = run([executable])
    (OUT / ('conversion-options-' + str(options) + '.txt')).write_text(result['stdout'] + result['stderr'])
    results['conversion_options_' + str(options)] = result['stdout'].splitlines()

red = run([BUILD / 'conversion-options-1', '--red-control'], expected=1)
assert 'window/GDK state accessed while option was off' in red['stderr']
(OUT / 'red-control.txt').write_text(red['stdout'] + red['stderr'])
results['red_control'] = 'Frozen unguarded baseline fails the off/no-state-read requirement (exit 1), as expected.'

app_old = original('app', 'src/slic3r/GUI/GUI_App.cpp')
app_new = candidate('app', 'src/slic3r/GUI/GUI_App.cpp')
startup = between(app_new, 'bool GUI_App::OnInit()\n{\n', '#ifdef __APPLE__')
added = startup.split('{\n', 1)[1]
assert app_new.replace(added, '', 1) == app_old
assert added.startswith('#if defined(__WXGTK3__) && wxUSE_SYSTEM_OPTIONS\n')
assert app_new.index('SetOption("gtk.window.font-dpi-scaling", 1)') < app_new.index('return on_init_inner();')
assert '#include <wx/sysopt.h>' in app_old
startup_probe = '''#include <cstring>
#include <cstdlib>
#include <iostream>
#include "wx/sysopt.h"
static int set_calls = 0;
#if wxUSE_SYSTEM_OPTIONS
void wxSystemOptions::SetOption(const wxString& name, int value) {
    if (name.text != "gtk.window.font-dpi-scaling" || value != 1) std::abort();
    ++set_calls;
}
#endif
class GUI_App {
public:
    bool OnInit();
    bool on_init_inner() { return set_calls == EXPECT_SET_CALLS; }
};
''' + startup + '''    return on_init_inner();
}
int main() {
    GUI_App app;
    if (!app.OnInit()) return 1;
    std::cout << "PASS: startup guard EXPECT_SET_CALLS=" << EXPECT_SET_CALLS
              << ", setter precedes simulated inner startup\\n";
}
'''
(BUILD / 'startup.cpp').write_text(startup_probe)
startup_logs = []
for label, defines, expected in [
    ('gtk3', ['-D__WXGTK3__', '-DwxUSE_SYSTEM_OPTIONS=1'], 1),
    ('gtk3-no-options', ['-D__WXGTK3__', '-DwxUSE_SYSTEM_OPTIONS=0'], 0),
    ('gtk2', ['-D__WXGTK20__', '-DwxUSE_SYSTEM_OPTIONS=1'], 0),
    ('windows', ['-D_WIN32', '-DwxUSE_SYSTEM_OPTIONS=1'], 0),
    ('macos', ['-D__APPLE__', '-DwxUSE_SYSTEM_OPTIONS=1'], 0),
]:
    executable = BUILD / ('startup-' + label)
    run(flags + defines + ['-DEXPECT_SET_CALLS=' + str(expected), BUILD / 'startup.cpp', '-o', executable])
    record = run([executable])
    startup_logs.append(label + ': ' + record['stdout'])
results['startup_guard'] = startup_logs
(OUT / 'startup-guards.txt').write_text(''.join(startup_logs))

# Verify that the actual guarded GTK block compiles to nothing without GTK3,
# using no GTK/wx declarations. This only checks preprocessing scope.
(BUILD / 'non-gtk3.cpp').write_text(new_block + '\nint main() { return 0; }\n')
run(flags + [BUILD / 'non-gtk3.cpp', '-o', BUILD / 'non-gtk3'])
run([BUILD / 'non-gtk3'])
results['non_gtk3_scope'] = 'Exact guarded wx block compiles and runs with no wx/GTK declarations when __WXGTK3__ is absent.'

# Apply/check only against scratch copies of the frozen files.
for project in ['wx', 'app']:
    target = OUT / 'applied' / project
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(OUT / 'original' / project, target)
    patch = OUT / (project + '-opt-in.patch')
    run(['git', 'apply', '--check', patch], cwd=target)
    run(['git', 'apply', patch], cwd=target)
    for file in (OUT / 'candidate' / project).rglob('*'):
        if file.is_file():
            rel = file.relative_to(OUT / 'candidate' / project)
            assert file.read_bytes() == (target / rel).read_bytes()
    run(['git', 'apply', '--reverse', '--check', patch], cwd=target)
    run(['git', 'apply', '--reverse', patch], cwd=target)
    for file in (OUT / 'original' / project).rglob('*'):
        if file.is_file():
            rel = file.relative_to(OUT / 'original' / project)
            assert file.read_bytes() == (target / rel).read_bytes()
results['patches'] = 'Both patches apply exactly to scratch copies of the specified frozen source, match candidates byte-for-byte, and reverse to originals.'

# Capture exact startup evidence for the parent; inspect call sites, not just line ordering.
startup_evidence = {}
for needle in ['bool GUI_App::OnInit()', 'SetOption("gtk.window.font-dpi-scaling", 1)',
               'return on_init_inner();', 'bool GUI_App::on_init_inner()',
               'preset_bundle = new PresetBundle();', 'mainframe = new MainFrame();',
               'scrn = new BBLSplashScreen(', 'RichMessageDialog',
               'if (! check_old_linux_datadir(GetAppName()))']:
    startup_evidence[needle] = [i for i, line in enumerate(app_new.splitlines(), 1) if needle in line]
results['source_startup_lines_candidate'] = startup_evidence
(OUT / 'extractions.json').write_text(json.dumps({
    'conversion_original': {'path': 'src/gtk/window.cpp', 'start_line': 4380,
                            'sha256': hashlib.sha256(old_block.encode()).hexdigest()},
    'conversion_candidate': {'path': 'src/gtk/window.cpp', 'start_line': 4380,
                             'sha256': hashlib.sha256(new_block.encode()).hexdigest()},
    'wrappers': {'path': 'include/wx/window.h', 'start_line': 996,
                 'sha256': hashlib.sha256(wrappers.encode()).hexdigest()},
    'rounding': {'path': 'include/wx/math.h', 'start_line': 137,
                 'sha256': hashlib.sha256(rounding.encode()).hexdigest()},
    'sysopt_header': {'path': 'include/wx/sysopt.h',
                      'sha256': hashlib.sha256(header.encode()).hexdigest()},
    'startup_prefix_candidate': {'path': 'src/slic3r/GUI/GUI_App.cpp', 'start_line': 2907,
                                 'sha256': hashlib.sha256(startup.encode()).hexdigest()},
}, indent=2) + '\n')
(OUT / 'verification.json').write_text(json.dumps(results, indent=2) + '\n')
print(json.dumps(results, indent=2))
