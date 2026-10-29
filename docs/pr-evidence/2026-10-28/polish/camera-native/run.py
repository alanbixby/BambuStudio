from pathlib import Path
import csv,json,os,subprocess,sys,resource
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
R=Path(__file__).resolve().parent;warm=Path('/home/bxb/.local/state/bambu-scaling/build-02.08.04.57')
(R/'fonts.conf').write_text('''<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd"><fontconfig><dir>/usr/share/fonts</dir><cachedir>'''+str(R/'font-cache')+'''</cachedir><include ignore_missing="yes">/etc/fonts/conf.d</include></fontconfig>''')
env=dict(os.environ,TMPDIR=str(R/'tmp'),XDG_CACHE_HOME=str(R/'cache'),XDG_CONFIG_HOME=str(R/'config'),XDG_DATA_HOME=str(R/'data'),XDG_STATE_HOME=str(R/'state'),XDG_RUNTIME_DIR=str(R/'runtime'),FONTCONFIG_FILE=str(R/'fonts.conf'),LD_LIBRARY_PATH=str(warm/'sysroot/usr/lib/x86_64-linux-gnu'),GDK_BACKEND='x11',GTK_THEME='Adwaita',GTK_OVERLAY_SCROLLING='0',GTK_USE_PORTAL='0',GSETTINGS_BACKEND='memory',NO_AT_BRIDGE='1',DBUS_SESSION_BUS_ADDRESS='unix:path='+str(R/'runtime/no-session-bus'),CAMERA_PRIVATE_XVFB='1')
for k in ['DISPLAY','WAYLAND_DISPLAY','XAUTHORITY','GTK_MODULES','GDK_DPI_SCALE','GDK_SCALE','WXGTK_DIP_SCALE','LD_PRELOAD']:env.pop(k,None)
if '--inside' not in sys.argv:
 cmd=['xvfb-run','-a','-e',str(R/'xvfb.log'),'-s','-screen 0 6000x4000x24 -dpi 96 -nolisten tcp','python3',str(R/'run.py'),'--inside']
 (R/'xvfb-command.json').write_text(json.dumps({'argv':cmd,'env_overrides':{k:v for k,v in env.items() if os.environ.get(k)!=v}},indent=2)+'\n')
 raise SystemExit(subprocess.run(cmd,cwd=R,env=env).returncode)
env['DISPLAY']=os.environ['DISPLAY'];env['XAUTHORITY']=os.environ['XAUTHORITY']
commands=[];results=[]
for scale in [1,2]:
 for dpi in [96,120,144]:
  for branch in ['none','web']:
   for height in [520,740]:
    for variant in ['old','new']:
     name=f'{variant}-dpi{dpi}-scale{scale}-{branch}-h{height}'
     cmd=[str(R/f'probe-{variant}'),str(dpi),branch,str(height)]
     commands.append({'name':name,'argv':cmd,'GDK_SCALE':scale,'DISPLAY':env['DISPLAY']})
     with (R/f'{name}.tsv').open('w') as out,(R/f'{name}.stderr').open('w') as err:
      proc=subprocess.run(cmd,cwd=R,env=dict(env,GDK_SCALE=str(scale)),stdout=out,stderr=err,timeout=30)
     rows=list(csv.DictReader((R/f'{name}.tsv').open(),delimiter='\t'))
     results.append({'name':name,'exit':proc.returncode,'rows':rows})
     (R/'raw-results.json').write_text(json.dumps(results,indent=2)+'\n')
     print(name,'exit',proc.returncode,'rows',len(rows),flush=True)
     if proc.returncode:raise SystemExit(proc.returncode)
(R/'run-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
