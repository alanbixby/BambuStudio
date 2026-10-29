from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
s=json.loads((R/'results.json').read_text());assert s['status']=='PASS'
heads={k:v['head'] for k,v in json.loads((R/'extraction.json').read_text()).items()}
heads['combined']='b7a379241d133f1808918aa9fc99caa1eeba3c79'
old=json.loads((R/'raw-results-compact.json').read_text())[0]['rows']
new=json.loads((R/'raw-results-compact.json').read_text())[1]['rows']
oldn=next(x for x in old if x['phase']=='narrow');newn=next(x for x in new if x['phase']=='narrow')
findings={'task':'Implementation verification of ASTRA-CAM-001 correction, not a new peer-review round','reviewed_heads':heads,'open_blocking_count':0,'new_findings':[], 'verified_findings':[{'id':'ASTRA-CAM-001','prior_severity':'blocking','severity':'non-blocking','status':'candidate_correction_verified_in_native_GTK_fixture','open':False,'source':{'repository':'/home/bxb/.t3-nightly/projects/bambu-studio-upstream','old_head':heads['old'],'candidate_head':heads['new'],'path':'src/slic3r/GUI/StatusPanel.cpp','old_line':2123,'candidate_lines':[2124,2125,2178]},'trigger':'Compact synthetic Control contents, camera min 574x288 DIP, 2200->1400 client DIP at unchanged 520-DIP frame client height; no AMS; private native wxGTK scroller.','outcome_old':'At 96 DPI / GDK_SCALE=1, actual client width 1385 but virtual width remains 2185, Control minimum 1581. Same excess persists after an extra queued fit; stable, no idle fit callbacks.','outcome_candidate':'Virtual width becomes 1385, Control minimum 781. At requested width1000, actual client985 retains required virtual1218. All six compact scale/DPI pairs reproduce the old fixed point and pass correction checks.','smallest_practical_fix':'Already present in candidate: client width minus exact three spacer widths, bounded by natural minima; FitInside after changed sizing. No further source change suggested by this test.','verification_performed':{'runs':s['total_runs'],'observations':s['total_observations'],'candidate_observations':s['total_candidate_observations'],'suite_results_file':'results.json','baseline_negative_control_file':'raw-results-compact.json','source':'probe-compact.cpp','reproduction':'COMMANDS.md'},'verification_still_needed':['Native Cocoa/MSW rendering and integration behavior, if those claims are needed.','Full application controls, media events/fullscreen lifecycle, WebView readiness/content-report timing are outside the disconnected fixture.'],'limits':s['limits']}], 'limitations':s['limits']}
(R/'findings.json').write_text(json.dumps(findings,indent=2)+'\n')
report=f'''# Camera correction — native implementation verification

**PASS within the disconnected GTK fixture. Open blocking findings from this implementation verification: 0.** The exact old function reproduces ASTRA-CAM-001's fixed point with compact synthetic controls; the exact candidate clears it. No new defect in the candidate was found in the measured cases. This is not an all-OS or merge-readiness claim, and it does not start another review round.

## Exact inputs

- Old PR 10: `{heads['old']}`.
- Candidate: `{heads['new']}`, `src/slic3r/GUI/StatusPanel.cpp:2061–2179`; changed budget at 2124–2125 and `FitInside()` at 2178.
- Combined app: `{heads['combined']}`. Its extracted function is byte-identical to the tested candidate (`combined-check.json`).
- Stable native wx archive supplied as wx `{ '3fea0af433d9630f79eaf8fbfc062364ba456be3' }`. Six archives and all wx headers were privately copied before compiling; input/copy hashes are in `provenance.json`. All six warm archive hashes were unchanged at final verification (`results.json`). The archive identification comes from the supplied build provenance; a compiled archive cannot independently establish its Git commit.

`prepare.py` reads source through exact `git show SHA:path`, then includes the entire unchanged function in each C++ executable. `extraction.json` records source lines and full-file/function hashes. The candidate and old function differ only in the intended row budget and final `FitInside()` call. Supporting panel/host and wx scroller source snapshots retain their SHA/path/hash records in `supporting-sources.json`.

## Method and matrix

Real wxGTK frames, wxScrolledWindow, wxPanels and native sizers run only on private Xvfb displays. The fixture follows the production outer structure: top/bottom spacers; horizontal left/middle/right spacers of 10 DIP each; expanding camera/title/feed/playbar/progress column; and non-expanding Control panel with a header and nested rows sizer. `SetSizerAndFit`, scroll rate25, native frame resizing, skipped size events, deferred `CallAfter` fitting, virtual-size refresh and pending native events all execute. There is no application build or launch.

{ s['total_runs'] } successful processes produced { s['total_observations'] } phase observations, including { s['total_candidate_observations'] } candidate observations:

- Standard fixture:48 processes — old/new × 96/120/144 DPI × GDK scale1/2 × no-AMS/web-shown × initial heights520/740 DIP. Its simple AMS stand-in only changes its minimum and uses ceil rounding. These web cases are preliminary geometry coverage, not full host behavior.
- Compact Control fixture:12 processes — old/new × all six scale/DPI pairs, no AMS, height520. Only synthetic Control content heights change (temp160, rack200, filament80 DIP), making the camera's 288-DIP feed minimum govern the row. This explicitly tests the arithmetic counterexample's geometric preconditions.
- AMS notification fixture:12 processes — old/new × all six scale/DPI pairs, web shown, height520. This stand-in starts at586×340 DIP, uses production-style `lround(FromDIP * zoom)`, reads base height back through `lround(minHeight / zoom)`, fixes min/max/current size and sends the production-style parent/grandparent Layout/SendSizeEvent notifications. Every candidate run reaches zoom1.35 after height growth and returns to1 after shrinking.

Every process measures wide2200 → narrow1400 → genuinely undersized1000 → natural boundary1218 → narrow1400 → wide2200, at unchanged initial height; then height1100 → initial height → narrow1400 → one extra queued fit. Actual client sizes, virtual extents, camera/Control allocations and minima, zoom, event counts and stability are retained in individual TSV files and `raw-results*.json`.

DPI is set before frames. `gtk.window.font-dpi-scaling=1` is set before wx startup as requested; the supplied pre-option archive may ignore the option. Recorded native `FromDIP(96)` values are96/120/144, independently of integer GDK scale1/2. Overlay scrolling is disabled on the private fixture. No window input is synthesized.

## Negative control and correction

At96 DPI / GDK scale1 in the compact fixture:

- Wide: actual client/virtual width2185, camera574×288, Control minimum1581.
- Narrow, old: client1385, virtual2185, Control minimum1581 — **800 unnecessary pixels**. The geometry stays stable with zero observed idle size/fit callbacks. After the later extra queued fit the old virtual width is2200, client1385; the bad fixed point persists.
- Narrow, candidate: client/virtual1385, Control minimum781. The camera minimum is preserved.
- Genuinely undersized, candidate: client985, virtual1218 (574 camera +614 natural Control +30 spacers). Required horizontal scrolling remains.
- Returning wide restores the original compact wide allocation. After grow/shrink and another narrowing, candidate virtual width again equals the fitting client width.

All six compact DPI/scale pairs reproduce persistent old excess and pass the correction. The taller standard fixture does **not** reproduce the same permanent minimum-height fixed point: its camera has more available height. Some old cases instead show temporary excess and repeated native resize callbacks during the observation window before later convergence. These cases are not reported as proof of an infinite loop or a permanent failure.

All candidate observations satisfy `virtualWidth <= max(clientWidth, naturalOuterMinimum)+1`, camera minimum enforcement, exact required scrolling in undersized phases, stable geometry, and no size/fit callbacks during a200ms quiet window following300ms of event pumping. Normal size/fit events while resizing are expected. This observes finite settling, not the absence of all wx idle events.

Height is not held artificially by the harness: native scrollbar appearance/removal can change client height. For example, compact old narrow client is1385×505 because it retains both bars; candidate is1385×520 after the unnecessary horizontal bar disappears. Vertical scrolling remains because the natural outer height is554. Tall/short AMS passes retain the existing height/zoom math; this test does not promise a new convergence rule for arbitrary content schedules.

## Limits and reproduction

`COMMANDS.md` contains the runnable sequence. All six focused compiler invocations succeeded; exact compile/link commands and logs are retained. Each corrected matrix process exited0; `python3 verify.py` passed. `results.json` contains assertions, raw metadata, per-suite counts and unchanged warm archive hashes. No repository/source/index/ref/GitHub/app/profile/printer mutations were performed. Output, compiler temp files, configs and font caches live here; Xvfb creates its normal ephemeral private-display socket. The user's DISPLAY and desktop were never used.

Media is a plain native panel returning an invalid size, so the **actual production 16:9 fallback** executes. There is no decoding/stream, fullscreen entry/exit, first-frame event dispatch, printer or network. The additional trigger is explicitly a queued function call, not a real media event. Title/header, other Control content and progress heights are fixed synthetic minima; they are not measured application widgets. The compact negative control establishes the exact native-wx failure mechanism under its stated conditions, without claiming those conditions were measured in the current installed application.

AMS is a native panel modeling a stable340-DIP report, not WebKit/WebView2. The notification fixture includes native size-event feedback, but not backend readiness, report timing, page visibility/recreation or DOM rendering. No-AMS executes the fitting math also used by the macOS no-zoom path; GTK execution does not verify Cocoa or MSW, which were neither compiled nor run. Later stream-aspect changes, fullscreen lifecycle and arbitrary AMS report schedules remain outside scope.

One exploratory AMS fixture initialization error was caught in the raw rows, corrected and rerun. Its excluded output and interruption are retained in `invalid-ams-initialization/`; they are not counted above. Read-only lookup corrections are recorded in `COMMANDS.md`. No source correction is requested by this verification.
'''
(R/'REPORT.md').write_text(report)
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and 'private-wx' not in p.parts and p.name!='manifest.json'}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Wrote REPORT.md, findings.json and artifact hash manifest')
