from pathlib import Path
import json,os,subprocess,resource
R=Path(__file__).resolve().parent
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for n in ['tmp','cache','config','data','state','runtime','font-cache']:(R/n).mkdir(exist_ok=True,mode=0o700)
env=dict(os.environ,TMPDIR=str(R/'tmp'),CCACHE_DISABLE='1',XDG_CACHE_HOME=str(R/'cache'),XDG_CONFIG_HOME=str(R/'config'),XDG_DATA_HOME=str(R/'data'),XDG_STATE_HOME=str(R/'state'),XDG_RUNTIME_DIR=str(R/'runtime'))
for k in ['DISPLAY','WAYLAND_DISPLAY','XAUTHORITY','LD_PRELOAD','CPATH','CPLUS_INCLUDE_PATH','C_INCLUDE_PATH','LIBRARY_PATH']:env.pop(k,None)
cmd=json.loads((R/'compile-command.json').read_text())
assert not any('/deps-build/' in x for x in cmd)
with (R/'compile.log').open('w') as f:p=subprocess.run(cmd,cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=60)
print('compiler exit',p.returncode)
if p.returncode:raise SystemExit(p.returncode)
deps=(R/'compile-dependencies.d').read_text()
assert '/deps-build/' not in deps
(R/'dependency-check.json').write_text(json.dumps({'compiler_exit':p.returncode,'no_deps_build_in_command':True,'no_deps_build_in_compiler_dependencies':True},indent=2)+'\n')
