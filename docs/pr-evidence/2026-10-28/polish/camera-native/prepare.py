from pathlib import Path
import subprocess, json, hashlib, shutil, time
R=Path(__file__).resolve().parent
repo='/home/bxb/.t3-nightly/projects/bambu-studio-upstream'
heads={'old':'fab83eef842e6967fa06d0bb05410940b4787d28','new':'010ae25289256dda9f0d09111cf24c28bdf44394'}
records={}
for variant,sha in heads.items():
 p='src/slic3r/GUI/StatusPanel.cpp'
 s=subprocess.check_output(['git','show',sha+':'+p],cwd=repo).decode()
 (R/f'StatusPanel-{variant}.cpp').write_text(s)
 start=s.index('void StatusBasePanel::fit_camera_to_feed()')
 end=s.index('\nStatusBasePanel::~StatusBasePanel()',start)
 fn=s[start:end]
 (R/f'fit-{variant}.inc').write_text(fn)
 records[variant]={'head':sha,'path':p,'line':s[:start].count('\n')+1,'file_sha256':hashlib.sha256(s.encode()).hexdigest(),'function_sha256':hashlib.sha256(fn.encode()).hexdigest()}
(R/'extraction.json').write_text(json.dumps(records,indent=2)+'\n')
prefix=Path('/home/bxb/.local/state/bambu-scaling/build-02.08.04.57/deps-build/destdir/usr/local')
D=R/'private-wx'; (D/'lib').mkdir(parents=True,exist_ok=True)
records={}
for name in ['libwx_gtk3u_core-3.1.a','libwx_baseu-3.1.a','libwxregexu-3.1.a','libjpeg.a','libpng16.a','libtiff.a']:
 s=prefix/'lib'/name; d=D/'lib'/name; before=s.stat(); shutil.copyfile(s,d)
 h=hashlib.sha256(s.read_bytes()).hexdigest(); after=s.stat()
 assert (before.st_size,before.st_mtime_ns,before.st_ino)==(after.st_size,after.st_mtime_ns,after.st_ino)
 assert h==hashlib.sha256(d.read_bytes()).hexdigest()
 records[name]={'source':str(s),'private_copy':str(d),'sha256':h,'size':after.st_size,'mtime_ns':after.st_mtime_ns}
shutil.copytree(prefix/'include/wx-3.1',D/'include/wx-3.1',dirs_exist_ok=True)
shutil.copytree(prefix/'lib/wx/include/gtk3-unicode-static-3.1',D/'lib/wx/include/gtk3-unicode-static-3.1',dirs_exist_ok=True)
(R/'provenance.json').write_text(json.dumps({'time':time.time(),'archives':records,'headers':{str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in D.rglob('*') if p.is_file() and p.suffix!='.a'},'stated_wx_head':'3fea0af433d9630f79eaf8fbfc062364ba456be3'},indent=2)+'\n')
print('extracted exact functions; privately copied and hashed six archives and wx headers')
