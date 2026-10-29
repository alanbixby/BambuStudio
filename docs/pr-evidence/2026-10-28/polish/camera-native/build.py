from pathlib import Path
import json, os, shlex, subprocess
R=Path(__file__).resolve().parent
warm=Path('/home/bxb/.local/state/bambu-scaling/build-02.08.04.57');prefix=warm/'deps-build/destdir/usr/local';D=R/'private-wx';sysroot=warm/'sysroot/usr'
for name in ['tmp','cache','config','data','state','runtime','font-cache']:(R/name).mkdir(exist_ok=True,mode=0o700)
env=dict(os.environ,TMPDIR=str(R/'tmp'),CCACHE_DISABLE='1',XDG_CACHE_HOME=str(R/'cache'),XDG_CONFIG_HOME=str(R/'config'),XDG_DATA_HOME=str(R/'data'),XDG_STATE_HOME=str(R/'state'),XDG_RUNTIME_DIR=str(R/'runtime'),PKG_CONFIG_PATH=f'{sysroot}/lib/x86_64-linux-gnu/pkgconfig:{sysroot}/share/pkgconfig')
for k in ['DISPLAY','WAYLAND_DISPLAY']:env.pop(k,None)
wxflags=shlex.split(subprocess.check_output([str(prefix/'bin/wx-config'),'--cxxflags'],env=env,text=True));wxflags=[f.replace(str(prefix),str(D)) for f in wxflags]
gtkflags=shlex.split(subprocess.check_output(['pkg-config','--cflags','gtk+-3.0'],env=env,text=True))
gtklibs=shlex.split(subprocess.check_output(['pkg-config','--libs','gtk+-3.0','libsecret-1'],env=env,text=True))
commands=[]
for variant in ['old','new']:
 cmd=['/usr/bin/c++','-std=c++17','-O0','-g','-DwxDEBUG_LEVEL=0','-DTEST_NEW='+str(int(variant=='new')),*wxflags,*gtkflags,str(R/'probe.cpp'),'-o',str(R/f'probe-{variant}'),*[str(D/'lib'/n) for n in ['libwx_gtk3u_core-3.1.a','libwx_baseu-3.1.a','libwxregexu-3.1.a','libjpeg.a','libpng16.a','libtiff.a']],*gtklibs,'-lfontconfig','-lpangoft2-1.0','-lSM','-lICE','-lX11','-lXext','-lz','-ldl','-lm','-pthread']
 commands.append(cmd)
 with (R/f'compile-{variant}.log').open('w') as log:p=subprocess.run(cmd,cwd=R,env=env,stdout=log,stderr=subprocess.STDOUT)
 print(variant,p.returncode,flush=True)
 if p.returncode:raise SystemExit(p.returncode)
(R/'compile-commands.json').write_text(json.dumps(commands,indent=2)+'\n')
