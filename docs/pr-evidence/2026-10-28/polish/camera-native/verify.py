from pathlib import Path
import json, hashlib
R=Path(__file__).resolve().parent
expected={'standard':48,'compact':12,'ams-events':12}
files={'standard':'raw-results.json','compact':'raw-results-compact.json','ams-events':'raw-results-ams-events.json'}
issues=[];suites={};negative_controls=[];all_candidates=[]
for name,fn in files.items():
 data=json.loads((R/fn).read_text());suite={'runs':len(data),'expected_runs':expected[name],'observations':sum(len(t['rows']) for t in data),'candidate_observations':0,'candidate_failures':[],'old_observations_with_excess_width':0,'old_unstable_observations':0,'old_idle_callbacks_observations':0}
 if len(data)!=expected[name]:issues.append(f'{name}: incomplete runs')
 for t in data:
  if t['exit']!=0 or len(t['rows'])!=10:issues.append(t['name']+': exit/row count')
  is_new='new-' in t['name']
  for row in t['rows']:
   r={k:(v if k=='phase' else float(v) if k=='zoom' else int(v)) for k,v in row.items()}
   width_excess=r['virtual_w']-max(r['client_w'],r['natural_w'])
   if is_new:
    suite['candidate_observations']+=1;all_candidates.append((t['name'],r))
    failed=[]
    if width_excess>1:failed.append('unnecessary_horizontal_extent')
    if not r['stable']:failed.append('unstable_geometry')
    if r['idle_size_events'] or r['idle_fit_calls']:failed.append('idle_resize_or_fit_callbacks')
    if r['camera_w']<r['camera_min_w']:failed.append('camera_below_natural_minimum')
    if name=='ams-events' and r['phase']=='height_grow' and r['zoom']<=1:failed.append('AMS_zoom_branch_not_exercised')
    if r['phase']=='too_narrow' and not (r['virtual_w']>r['client_w'] and abs(r['virtual_w']-r['natural_w'])<=1):failed.append('required_scroll_not_preserved')
    if r['phase'] in ['narrow','narrow_again','wide_again','narrow_after_height','narrow_after_explicit_trigger'] and r['client_w']>=r['natural_w'] and abs(r['virtual_w']-r['client_w'])>1:failed.append('fitting_client_does_not_match_virtual_width')
    if failed:suite['candidate_failures'].append({'run':t['name'],'phase':r['phase'],'failed':failed,'row':r})
   else:
    suite['old_observations_with_excess_width']+=int(width_excess>1)
    suite['old_unstable_observations']+=int(not r['stable'])
    suite['old_idle_callbacks_observations']+=int(bool(r['idle_size_events'] or r['idle_fit_calls']))
    if name=='compact' and r['phase'] in ['narrow','narrow_after_explicit_trigger']:
     negative_controls.append({'run':t['name'],'phase':r['phase'],'excess_px':width_excess,'stable':r['stable'],'idle_callbacks':r['idle_fit_calls'],'client_w':r['client_w'],'virtual_w':r['virtual_w']})
 if suite['candidate_failures']:issues.append(name+': candidate assertions failed')
 suites[name]=suite
assert len(negative_controls)==12
if not all(n['excess_px']>0 and n['stable']==1 and n['idle_callbacks']==0 for n in negative_controls):issues.append('compact negative control not reproduced')
metadata=[]
for p in sorted(R.glob('*.stderr')):
 text=p.read_text();metadata.append({'file':p.name,'text':text})
 if 'variant=' not in text:issues.append(p.name+': missing metadata')
 if any(s in text for s in ['CRITICAL','WARNING','assert','Segmentation']):issues.append(p.name+': native diagnostic')
if len(metadata)!=72:issues.append('stderr metadata count')
archive_state=[]
for name,x in json.loads((R/'provenance.json').read_text())['archives'].items():
 h=hashlib.sha256(Path(x['source']).read_bytes()).hexdigest()
 archive_state.append({'name':name,'unchanged':h==x['sha256'],'before_sha256':x['sha256'],'after_sha256':h})
 if h!=x['sha256']:issues.append(name+': warm input changed')
summary={'status':'PASS' if not issues else 'FAIL','issues':issues,'suites':suites,'total_runs':sum(s['runs'] for s in suites.values()),'total_observations':sum(s['observations'] for s in suites.values()),'total_candidate_observations':len(all_candidates),'compact_negative_controls':negative_controls,'warm_archives_after_test':archive_state,'metadata':metadata,'limits':['GTK3 private Xvfb native scrollers/sizers; not Cocoa/MSW rendering.','Media is a plain panel returning invalid video size, exercising production 16:9 fallback.','Other content/header/progress minima are fixed synthetic fixtures; no claim those heights were measured in the app.','AMS is synthetic native panel; fixed 340 DIP page content; no WebView, readiness, network, device or report timing test.','Geometry stability means unchanged geometry and no size/fit callbacks during 200ms quiet window after 300ms settlement; not a claim of zero idle events.','Tall and compact synthetic content profiles intentionally differ and are reported separately.']}
(R/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['status','issues','total_runs','total_observations','total_candidate_observations','suites']},indent=2))
raise SystemExit(bool(issues))
