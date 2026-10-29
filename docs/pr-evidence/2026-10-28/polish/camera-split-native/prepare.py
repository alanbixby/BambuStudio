from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parent
B=R.parent/'camera-native'
REPO=Path('/home/bxb/.t3-nightly/projects/bambu-studio-upstream')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory():
 return {str(p.relative_to(B)):{'sha256':digest(p),'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in sorted(B.rglob('*')) if p.is_file()}
# Original inputs are read only. Never run the original prepare/build/verify scripts.
(R/'original-before.json').write_text(json.dumps(inventory(),indent=2)+'\n')
curated=Path('/tmp/bambu-polish-20261028/curated-prs.json')
row=next(x for x in json.loads(curated.read_text()) if x['key']=='bambu-10')
sha=row['head']; assert sha=='bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7'
records={}
for ext in ['cpp','hpp']:
 path='src/slic3r/GUI/StatusPanel.'+ext
 blob=subprocess.check_output(['git','show',sha+':'+path],cwd=REPO)
 (R/('StatusPanel.'+ext)).write_bytes(blob)
 records[ext]={'head':sha,'path':path,'sha256':hashlib.sha256(blob).hexdigest()}
s=(R/'StatusPanel.cpp').read_text()
a=s.index('void StatusBasePanel::fit_camera_to_feed()')
b=s.index('\nStatusBasePanel::~StatusBasePanel()',a)
fn=s[a:b]
assert 'AMS' not in fn and 'ams_' not in fn and '#if' not in fn
(R/'fit-camera-only.inc').write_text(fn)
records['function']={'sha256':digest(R/'fit-camera-only.inc'),'start_line':s[:a].count('\n')+1,'line_count':len(fn.splitlines()),'unmodified_extraction':True}
(R/'extraction.json').write_text(json.dumps(records,indent=2)+'\n')
s=(B/'probe-compact.cpp').read_text()
s=s.replace('#define BBL_ENABLE_AMS_CONTROL_WEB 1\n','')
s=s.replace(' double zoom=1;',' double zoom=1;\npublic:\n int zoomSetCalls=0;')
s=s.replace('void SetFitZoom(double z) { zoom=z;', 'void SetFitZoom(double z) { ++zoomSetCalls; zoom=z;')
s=s.replace('m_ams_control_web_panel','fixture_ams_panel')
s=s.replace('#if TEST_NEW\n#include "fit-new.inc"\n#else\n#include "fit-old.inc"\n#endif','#include "fit-camera-only.inc"')
s=s.replace('int natural=p->m_camera_media_sizer->CalcMin().x+p->FromDIP(614)+3*p->FromDIP(10);','int naturalControl=p->m_machine_ctrl_panel->GetSizer()->CalcMin().x;\n  int natural=p->m_camera_media_sizer->CalcMin().x+naturalControl+3*p->FromDIP(10);')
s=s.replace('stable\\n"','stable\\tcontrol_natural_w\\tcontrol_expected_natural_w\\tams_zoom_set_calls\\n"')
s=s.replace('<<(before==geometry(p))<<\'\\n\';','<<(before==geometry(p))<<\'\\t\'<<naturalControl<<\'\\t\'<<p->FromDIP(614)<<\'\\t\'<<p->fixture_ams_panel->zoomSetCalls<<\'\\n\';')
assert 'control_natural_w' in s and 'zoomSetCalls' in s and 'fit-new.inc' not in s
(R/'probe-camera-only.cpp').write_text(s)
cmd=json.loads((B/'compile-commands-compact.json').read_text())[1]
cmd=[x.replace(str(B/'probe-compact.cpp'),str(R/'probe-camera-only.cpp')).replace(str(B/'probe-compact-new'),str(R/'probe-camera-only')) for x in cmd]
cmd[1:1]=['-MD','-MF',str(R/'compile-dependencies.d')]
assert not any('/deps-build/' in x for x in cmd)
(R/'compile-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
provenance=json.loads((B/'provenance.json').read_text())
archives={n:{'path':str(B/'private-wx/lib'/n),'sha256':digest(B/'private-wx/lib'/n),'matches_sealed_provenance':digest(B/'private-wx/lib'/n)==v['sha256']} for n,v in provenance['archives'].items()}
headers={str(p.relative_to(B/'private-wx')):digest(p) for p in sorted((B/'private-wx').rglob('*')) if p.is_file() and p.suffix!='.a'}
assert all(v['matches_sealed_provenance'] for v in archives.values())
assert headers==provenance['headers']
(R/'inputs.json').write_text(json.dumps({'curated_manifest_sha256':digest(curated),'source':records,'reference_probe_sha256':digest(B/'probe-compact.cpp'),'fixture_sha256':digest(R/'probe-camera-only.cpp'),'sealed_provenance_sha256':digest(B/'provenance.json'),'stated_wx_head':provenance['stated_wx_head'],'archives':archives,'headers':headers,'header_manifest_sha256':hashlib.sha256(json.dumps(headers,sort_keys=True).encode()).hexdigest()},indent=2)+'\n')
print('Extracted camera-only helper and adapted read-only compact fixture; sealed archives/headers match original provenance.')
