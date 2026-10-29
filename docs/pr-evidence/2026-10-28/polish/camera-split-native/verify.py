from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parent;B=R.parent/'camera-native'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
raw=json.loads((R/'raw-results.json').read_text())
issues=[];observations=[]
expected={(dpi,scale,'none') for dpi in [96,144,192] for scale in [1,2]}|{(96,1,'web'),(192,2,'web')}
actual=set()
phases=['wide','narrow','too_narrow','natural_boundary','narrow_again','wide_again','height_grow','height_shrink','narrow_after_height','narrow_after_explicit_trigger']
for t in raw:
 match=re.fullmatch(r'camera-only-dpi(\d+)-scale(\d+)-(none|web)-h520',t['name'])
 if not match:issues.append({'run':t['name'],'error':'unexpected_run_name'});continue
 dpi,scale,ams=int(match[1]),int(match[2]),match[3];actual.add((dpi,scale,ams))
 if t['exit']!=0 or [r['phase'] for r in t['rows']]!=phases:issues.append({'run':t['name'],'error':'exit_or_phases'})
 for row in t['rows']:
  r={k:(v if k=='phase' else float(v) if k=='zoom' else int(v)) for k,v in row.items()}
  failed=[]
  if r['virtual_w']>max(r['client_w'],r['natural_w'])+1:failed.append('unnecessary_horizontal_extent')
  if not r['stable']:failed.append('geometry_did_not_settle')
  if r['idle_size_events'] or r['idle_fit_calls']:failed.append('callbacks_during_quiet_window')
  if r['camera_w']<r['camera_min_w']:failed.append('camera_below_natural_minimum')
  if r['control_natural_w']!=r['control_expected_natural_w']:failed.append('natural_control_minimum_changed')
  if r['zoom']!=1 or r['ams_zoom_set_calls']!=0:failed.append('camera_only_set_AMS_zoom')
  if r['phase']=='too_narrow' and not (r['virtual_w']>r['client_w'] and abs(r['virtual_w']-r['natural_w'])<=1):failed.append('required_natural_scroll_missing')
  if r['client_w']>=r['natural_w'] and abs(r['virtual_w']-r['client_w'])>1:failed.append('fitting_viewport_has_horizontal_extent')
  record={'run':t['name'],**r,'unnecessary_width_px':max(0,r['virtual_w']-max(r['client_w'],r['natural_w'])),'failures':failed}
  observations.append(record)
  if failed:issues.append(record)
 stderr=(R/(t['name']+'.stderr')).read_text()
 m=re.fullmatch(r'variant=1 dpi=(\d+) fromdip96=(\d+) gdk_scale=(\d+) display=(:\d+) ams=([01]) initial_h=520\n',stderr)
 if not m or (int(m[1]),int(m[2]),int(m[3]),int(m[5]))!=(dpi,dpi,scale,int(ams=='web')):issues.append({'run':t['name'],'error':'unexpected_native_metadata','stderr':stderr})
 if t['rows']:
  first,last=t['rows'][0],next(x for x in t['rows'] if x['phase']=='wide_again')
  for key in ['client_w','virtual_w','camera_w','control_w','control_min_w']:
   if first[key]!=last[key]:issues.append({'run':t['name'],'error':'wide_geometry_not_restored','field':key})
if len(raw)!=8 or actual!=expected:issues.append({'error':'incomplete_or_duplicate_matrix'})
original_before=json.loads((R/'original-before.json').read_text())
original_after={str(p.relative_to(B)):{'sha256':digest(p),'size':p.stat().st_size,'mtime_ns':p.stat().st_mtime_ns} for p in sorted(B.rglob('*')) if p.is_file()}
(R/'original-after.json').write_text(json.dumps(original_after,indent=2)+'\n')
changes=[k for k in sorted(set(original_before)|set(original_after)) if original_before.get(k)!=original_after.get(k)]
if changes:issues.append({'error':'original_files_changed','files':changes})
inputs=json.loads((R/'inputs.json').read_text())
for name,entry in inputs['archives'].items():
 if digest(Path(entry['path']))!=entry['sha256']:issues.append({'error':'sealed_private_archive_changed','name':name})
if digest(R/'fit-camera-only.inc')!=inputs['source']['function']['sha256']:issues.append({'error':'extracted_function_changed'})
if digest(R/'probe-camera-only.cpp')!=inputs['fixture_sha256']:issues.append({'error':'fixture_changed'})
limits=[
'GTK3 native wx scrollers/sizers on private Xvfb only; neither Cocoa/MSW nor full Bambu was compiled or run.',
'Control content, title, playbar and progress are fixed synthetic native panels. Hidden AMS uses the original short compact Control profile; shown AMS substitutes a taller fixed 586x340 DIP panel.',
'Media is a disconnected wxPanel returning invalid video size, exercising the actual production 16:9 fallback; no decoding, first-frame lifecycle, fullscreen, printer or network.',
'AMS is a native fixed panel with a spy setter, not a browser/DOM/backend. Zero setter calls and zoom 1 are asserted, including height growth.',
'Finite settling observation: 300ms nominal event pumping then 200ms quiet observation per phase; does not prove absence of all idle events or behavior under arbitrary future events.',
'Sealed private wx headers/archives match original provenance. The archive commit identity is supplied provenance, not independently established from archive bytes. No warm deps-build headers, archives or wx-config were accessed.',
'Recorded non-wx GTK/system sysroot include and shared-library paths were reused read-only. System GTK libraries are outside the sealed wx archive set.',
'Prior 72-process proof and negative controls were not rerun or incorporated into this new run count.'
]
result={'status':'PASS' if not issues else 'FAIL','source_head':inputs['source']['cpp']['head'],'total_processes':len(raw),'total_observations':len(observations),'hidden_AMS_processes':sum('-none-' in t['name'] for t in raw),'shown_unzoomed_AMS_processes':sum('-web-' in t['name'] for t in raw),'font_DPI':[96,144,192],'GDK_scale':[1,2],'issues':issues,'original_files_checked':len(original_before),'original_files_unchanged':not changes,'original_changed_files':changes,'maximum_unnecessary_horizontal_extent_px':max(x['unnecessary_width_px'] for x in observations),'quiet_size_callbacks':sum(x['idle_size_events'] for x in observations),'quiet_fit_callbacks':sum(x['idle_fit_calls'] for x in observations),'maximum_AMS_zoom_set_calls':max(x['ams_zoom_set_calls'] for x in observations),'natural_control_minimum_preserved':all(x['control_natural_w']==x['control_expected_natural_w'] for x in observations),'observations':observations,'limits':limits}
(R/'results.json').write_text(json.dumps(result,indent=2)+'\n')
(R/'findings.json').write_text(json.dumps({'status':result['status'],'open_findings':issues,'scope':'focused implementation verification of extracted camera-only helper; no peer-review round','limits':limits},indent=2)+'\n')
artifacts=['StatusPanel.cpp','StatusPanel.hpp','fit-camera-only.inc','probe-camera-only.cpp','probe-camera-only','prepare.py','build.py','run.py','verify.py','compile-command.json','compile-dependencies.d','inputs.json','original-before.json','original-after.json','results.json','findings.json']
(R/'artifact-hashes.json').write_text(json.dumps({n:digest(R/n) for n in artifacts},indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['observations','limits']},indent=2))
raise SystemExit(bool(issues))
