#!/usr/bin/env python3
"""Read frozen Git objects; write candidate files and unified patches only here."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
WX = Path('/home/bxb/.t3-nightly/projects/bambu-wx-upstream')
APP = Path('/home/bxb/.t3-nightly/projects/bambu-studio-upstream')
WX_SHA = '3fea0af433d9630f79eaf8fbfc062364ba456be3'
APP_SHA = '0b34fcad456618e5d023e4f475dffb3f75ae6472'
records = []

def read(repo, sha, path):
    args = ['git', '-C', str(repo), 'show', sha + ':' + path]
    result = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    records.append({'argv': args, 'exit_code': result.returncode,
                    'stdout_sha256': hashlib.sha256(result.stdout).hexdigest()})
    return result.stdout.decode('utf-8')

def save(path, contents):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(contents.encode('utf-8'))

def replace_once(text, old, new):
    assert text.count(old) == 1
    return text.replace(old, new)

original = {}
for repo, sha, name, paths in [
    (WX, WX_SHA, 'wx', ['src/gtk/window.cpp', 'interface/wx/window.h',
                       'interface/wx/sysopt.h', 'include/wx/window.h',
                       'include/wx/sysopt.h', 'include/wx/math.h', 'src/common/sysopt.cpp',
                       'src/common/wincmn.cpp']),
    (APP, APP_SHA, 'app', ['src/slic3r/GUI/GUI_App.cpp']),
]:
    for path in paths:
        text = read(repo, sha, path)
        original[name, path] = text
        save(OUT / 'original' / name / path, text)

updated = {}
path = 'src/gtk/window.cpp'
updated['wx', path] = replace_once(original['wx', path],
    'double wxGTKDIPScale(const wxWindowBase* window)\n{\n',
    'double wxGTKDIPScale(const wxWindowBase* window)\n{\n'
    '    // Keep legacy applications on identity conversions unless they opt in.\n'
    '    if ( wxSystemOptions::GetOptionInt("gtk.window.font-dpi-scaling") != 1 )\n'
    '        return 1;\n\n')
path = 'interface/wx/window.h'
updated['wx', path] = replace_once(original['wx', path],
    '        In this wxGTK3 fork, the conversion also follows the GTK screen font\n'
    '        resolution. GetDPIScaleFactor() and GetContentScaleFactor() still report\n'
    '        the integer window scale, so fractional font DPI can make them differ\n'
    '        from the scale used here.\n',
    '        In this wxGTK3 fork, the conversion follows the GTK screen font\n'
    '        resolution only when the wxSystemOptions option\n'
    '        @c gtk.window.font-dpi-scaling is set to 1 (default: 0).\n'
    '        GetDPIScaleFactor() and GetContentScaleFactor() still report the\n'
    '        integer window scale, so fractional font DPI can make them differ\n'
    '        from the scale used here.\n')
path = 'interface/wx/sysopt.h'
updated['wx', path] = replace_once(original['wx', path],
    '    @flag{gtk.window.force-background-colour}\n',
    '    @flag{gtk.window.font-dpi-scaling}\n'
    '        GTK3 only. If 1, wxWindow::FromDIP() and wxWindow::ToDIP() follow\n'
    '        the screen font resolution. Default: 0 (identity conversions).\n'
    '        Set before creating windows and do not change it afterwards.\n'
    '    @flag{gtk.window.force-background-colour}\n')
path = 'src/slic3r/GUI/GUI_App.cpp'
updated['app', path] = replace_once(original['app', path],
    'bool GUI_App::OnInit()\n{\n',
    'bool GUI_App::OnInit()\n{\n'
    '#if defined(__WXGTK3__) && wxUSE_SYSTEM_OPTIONS\n'
    '    // Enable font-DPI geometry before startup creates any windows.\n'
    '    wxSystemOptions::SetOption("gtk.window.font-dpi-scaling", 1);\n'
    '#endif\n\n')

stats = {}
for name in ['wx', 'app']:
    chunks = []
    for (project, path), text in updated.items():
        if project != name:
            continue
        save(OUT / 'candidate' / name / path, text)
        chunks.append('diff --git a/{0} b/{0}\n'.format(path))
        chunks.extend(difflib.unified_diff(original[name, path].splitlines(True),
                      text.splitlines(True), fromfile='a/' + path, tofile='b/' + path))
    patch = ''.join(chunks)
    save(OUT / (name + '-opt-in.patch'), patch)
    stats[name] = {'additions': sum(s.startswith('+') and not s.startswith('+++') for s in patch.splitlines()),
                   'deletions': sum(s.startswith('-') and not s.startswith('---') for s in patch.splitlines())}

(OUT / 'prepare-commands.json').write_text(json.dumps(records, indent=2) + '\n')
(OUT / 'patch-stats.json').write_text(json.dumps(stats, indent=2) + '\n')
print(json.dumps(stats, indent=2))
