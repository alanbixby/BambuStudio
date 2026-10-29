# Astra — camera / temperature, new loop round 1

**Open blocking findings: 1 (ASTRA-CAM-001, PR 10).** No new blocking finding in PR 9. Two non-blocking review/documentation findings follow. No changes outside this output directory, no delegation, builds, GUI interaction, printer operations, GitHub writes, or application launch.

## Exact scope

- App base: `79df7ae309be398ed30c9f397c13c9911c2edc57`.
- PR 9: `e51f9b9c4aa1489fcf73e3a9dc0b7e454cd8db37` (80 additions / 21 deletions, 2 files).
- PR 10: `fab83eef842e6967fa06d0bb05410940b4787d28` (219 additions / 3 deletions, 6 files).
- Combined app: `1f880d3cd36e0317ff6535a7a089a30f079a4042`. PR 9's two files, PR 10's host/panel files, and the exact `fit_camera_to_feed()` method match the reviewed heads.
- wx upstream checked: `abb542694ef4534a50e65c5b877b2774d02952ae`, compared with old upstream `e2fa9bda52f720242e35def30ac4a01fbe75f5a8` and combined `3fea0af433d9630f79eaf8fbfc062364ba456be3`.
- Frozen PR descriptions: `/tmp/bambu-polish-20261028/round1/bambu-{09,10}-body.md`, cross-checked with `live-prs.json`.

All source reads used `git show SHA:path`, `git grep SHA`, or immutable endpoint diffs. `sources.json` records 32 source snapshots. Historical reviews were read as leads, not accepted as proof.

## ASTRA-CAM-001 — blocking — old virtual width can pin an oversized Control column after narrowing

**Location:** PR 10, `src/slic3r/GUI/StatusPanel.cpp:2123`, `2154–2157`, `2165–2175`; scrolled-window construction at `1953–1956`. Backend evidence: wx `abb54269`, `src/generic/scrlwing.cpp:187–209,760–818`; `src/common/wincmn.cpp:952–958`.

**Trigger:** Start with a wide, short Status page, then narrow it while the camera is height-limited. The cleanest case is a hidden/non-web AMS panel (also the solver branch used on macOS), with the camera at its normal 288-pixel minimum at 100% scaling. This does not need a playing stream: the code supplies 16:9 when no video size is available.

**Failure:** `row_width` is the sum of the laid-out child widths. `StatusBasePanel` is a `wxScrolledWindow`, so these are allocations inside the **virtual** area, not necessarily the visible client area. The previous fit installs spare width as an explicit minimum on the Control panel. On narrowing, wx's size handler computes the new virtual extent from that old minimum, then the deferred fit reads it back as available width. `Layout()` does not recompute virtual size, and the fit may return immediately because its target is unchanged.

A particularly simple fixed point, excluding unchanged outer/middle spacers:

- Camera minimum width 574, natural Control width 614, available camera height 288, wide row 2200.
- At 16:9 the ideal feed is 512 wide; the actual camera minimum clamps it to 574. The fit installs Control minimum **1626**.
- Narrow the client row to 1400. Its natural contents need only 574 + 614 = 1188.
- wx computes virtual row width `max(1400, 574 + 1626) = 2200`.
- The fit reads 2200 again, chooses 1626 again, and returns. The page keeps **800 unnecessary pixels of horizontal scroll range**; the Control content/header can sit beyond the visible right edge.
- A viewport-based fit would choose Control width 826 and fit the row into 1400.

This is not the documented acceptance of centered margins in short windows: the stale minimum prevents using the smaller visible window at all. It is also not merely slow convergence; the 288-height case is a fixed point even if more size events or `FitInside()` calls arrive. At greater heights, the absent virtual-size refresh produces a related stale-layout case (374-height fixture: virtual row 2109 versus client 1400).

**Reproduction/evidence:** `python3 -I resize_counterexample.py` passes nine source-derived arithmetic/event counterexamples; results are in `resize_counterexample.json`. The script asserts the relevant production statements and follows wx's size/virtual-layout sequence. Fixture natural widths/heights are explicit inputs, not claimed native measurements. This is an algorithmic counterexample grounded in actual wx code, **not a native GUI test**. The camera minimum 574 × 288 is from `StatusPanel.cpp:574,2370`; alternative natural widths 602/614/700 reproduce the same problem.

**Smallest practical fix:** Calculate the usable row budget from the current client width minus the existing fixed spacers, bounded by the *natural* camera/Control minima. Do not use the previously enlarged child allocations as the available budget. After changing a minimum, refresh the scrolled virtual extent with the existing `FitInside()` idiom as needed. `FitInside()` alone cannot fix the fixed point above. No new cache, general layout abstraction, or persistent solver state is needed.

**Verification needed:** Repeat wide → narrow at unchanged short height, both with web AMS hidden and with it shown; include macOS's no-zoom branch. Verify the horizontal virtual extent returns to the natural minimum/client width without requiring an unrelated machine update. Cover 100% and fractional DPI, genuinely undersized windows that still need scrolling, and fullscreen exit. A disconnected native harness or app session is needed to validate actual scrollbar/event behavior after the correction.

## ASTRA-CAM-002 — non-blocking — earlier camera models assume page reports production does not send

**Evidence:** PR 10's unchanged `src/slic3r/GUI/DeviceWeb/device_page/src/features/device-page/ams-control-web/AmsControlWebPage.tsx:23–39,119–128`, `geometry.ts:116–141`, and `dip.ts:4–20`. Compare historical `round3/camera_fable/REPORT.md` (CF-10/CF-11 and “content_size page script is not in the repository”) and `pending_zoom_model_r3.py`.

The page source *is* in this commit. It sends a fixed width 586 and a height computed from visible bands. The hook sends only a positive **changed height**; it does not observe window resize, zoom, or DOM height. The full visible slot-body combinations are 233, 249, 270, 286, 287, 303, 324, and 340 CSS pixels. Missing slot-body combinations are below the host's 220 minimum. Thus the prior synthetic 336/344-near-340 jitter cases are not current production combinations. Nor does widening the WebView2 startup viewport cause the page to report a width-dependent 260 height and then a correcting 340 height solely because zoom changed.

**Trigger/outcome:** Treating these synthetic schedules as observed/current production behavior makes the review record and startup caveats harder to trust. It can also hide real missing triggers, such as unchanged-height DPI transitions, which the synthetic model supplies extra reports to resolve.

**Smallest fix:** Correct the evidence record to distinguish stress inputs from actual reachable page reports. Remove or qualify CF-10/CF-11's production implications and the missing-source assertion. Keep the valid startup pending-zoom check: the first real page report necessarily occurs after the browser exists, and the host applies zoom **before** its height-jitter early return (`DeviceWebHost.cpp:618–631`). No production change is requested for this finding.

**Verification:** Trace the actual hook → bridge → host path, use real band-height combinations for production claims, and label any additional synthetic cases as robustness exploration. Do not infer resize-triggered reports from a generic WebView model.

## ASTRA-DOC-001 — non-blocking — consolidate the repeated PR validation caveats

**Evidence:** Frozen PR 10 body lines 5,12,14,16,18,20; PR 9 lines 3,5,10,12,14. Frozen body word counts are approximately 274 and 185, including Markdown tokens. Both contain two screenshot attachments.

**Trigger/outcome:** A reviewer reaches multiple paragraphs saying the screenshots use a combined older build and Windows/macOS were not run. PR 10 also narrates successive review fixes and model counts. PR 9 mentions internal helper implementation and absence of Objective-C ABI code, which does little to explain the user-facing behavior.

**Smallest fix:** Keep one behavior paragraph, one compact validation paragraph with exact limitations, the two screenshots with one shared provenance caption, and one evidence link. Retain the fork/upstream approval boundary. Put model counts and startup implementation history in the evidence record. Remove the repeated “Screenshots predate…” paragraph by combining it with the first provenance caption. This is editorial, not an unverified claim that coverage improved.

**Verification:** Compare rewritten bodies against frozen facts; keep screenshots and their historical/combined-build attribution; do not imply the unlaunched latest artifact was tested or that Windows/macOS passed.

## PR 9 independent technical review

No new blocker found at this head.

- `TempInput.cpp:394–408` uses the native sizing API for editing and for idle MSW/Cocoa. wx MSW `textctrl.cpp:663–690,2700–2754` sets both default font margins and includes one margin plus caret allowance; `textentry.cpp:1055–1062` returns the left margin. Adding it once more is consistent with this control's default equal-margin configuration. No inspected caller overrides those margins.
- Cocoa `textctrl_osx.cpp:192–244` adds four horizontal and two vertical pixels for these positive text extents. The right-aligned borderless field is supported by `cocoa/textctrl.mm`'s field creation path. GTK3 `control.cpp:95–102` removes CSS padding/border; `textctrl.cpp:2091–2149` adds nine horizontal pixels when sizing the editing field. GTK idle retains the previously verified glyph-only geometry. These code contracts do not substitute for a native caret/selection test.
- Focus relays the existing parent observer, marks editing, and lays out before clearing `_`. Text events relayout only while idle. Programmatic `SetTagTemp` still uses `SetValue` then `messureSize`; the added handler only reads the value and changes geometry. Blur clears the editing geometry before the existing warning/reset/finish path. Enter validates before posting the finish event and uses the existing navigation guard.
- The parent click handler checks `m_read_only` and `IsEnabled()` and only requests focus. It does not submit a temperature. The geometry methods do not change warning validation or target values. Parent finish handlers still read the actual native entry value; native event ordering and printer command policy are unchanged baseline logic.
- Both minimum calculations use editing size. Right alignment anchors the outer target/unit column; native glyph gaps may differ by platform, as the body already says. The minimum calculation includes all three four-DIP gaps, both insets, icons/current text/slash/entry/unit. `Rescale()` runs the same measurement path.
- **Baseline defects, not PR 9 regressions:** `SetReadOnly` only flips a bool (`TempInput.hpp:100`) and suppresses mouse entry; it does not call `SetEditable(false)`. Keyboard focus/programmatic focus are not made truly read-only by that setter. Blur already posts a finish event independently of validation, and the parent performs existing clamping/submission. These should not be mistaken for new safeguards provided by the alignment PR. No keyboard or printer repro was attempted.

## Camera compatibility, lifecycle, and limits

- **WebView2 readiness:** wx `abb54269` assigns the core view and controller in the same creation callback before event registration/navigation (`webview_edge.cpp:379–466`). `GetNativeBackend()` returns the core view (`:824`); `Get/SetZoomFactor` dereference the controller (`:715–724`). The host guard is meaningful and the first real positive content report applies a pending zoom before jitter filtering. Synthetic 340 startup sizing keeps host/panel minimum and `m_fit_zoom` consistent before that report.
- **Latest wx change:** `e2fa9bda..abb54269` only adds ten lines in `UpdateBounds()` (`:173–186`), querying controller3, disabling automatic monitor-scale detection, and assigning `GetDPIScaleFactor()` as rasterization scale. The readiness and zoom APIs are unchanged. The interface query is conditional. This changes Windows text-scale handling; native compilation and monitor migration were not tested here.
- **macOS:** Both the solver's AMS selection/update and the host zoom call exclude `__WXOSX__`. wx `webview_webkit.mm:619–626` implements magnification, confirming the reason. Camera fitting remains active and therefore still needs the ASTRA-CAM-001 correction there.
- **GTK:** `webview_webkit2.cpp:1033–1041` forwards zoom to WebKit's zoom level. CSS report dimensions are multiplied by `FromDIP` and the fit factor once. Existing combined-wx font-DPI semantics matter; do not multiply integer GDK content scale again. This review did not repeat the historical real-WebKit scaling probe.
- **DPI baseline limitation:** `DeviceWebHost::OnHostShown` (`:341–346`) only updates health monitoring; `msw_rescale` (`:721–723`) is empty. There is no automatic reapplication of `m_last_logical_content_size` on show despite its header comment. The page does not resend unchanged heights after DPI/zoom changes. AMS sizing can therefore remain stale until a content-height or fit-zoom change. This missing rescale path predates PR 10; it is not a newly assigned blocker. Avoid a monitor-migration compatibility claim. A separate small fix should use the existing host sizing method from an actual rescale trigger, rather than add a DPI cache.
- **Fullscreen/lifetime:** Fits return while fullscreen. Exit restores the sizer item before queuing a fit. `CallAfter` is queued on the Status object, and wx removes its pending events during handler destruction (`event.h:3748–3750`, `event.cpp:1156–1191`). No new raw-capture use-after-free is demonstrated. Media first-frame handling calls `Skip()`, preserving the existing handler chain. `GetVideoSize()` locks its mutex. A stream-resolution update does not emit another first-frame event; the already disclosed later-trigger limitation remains.
- **Fast visibility:** Fits inspect current `IsShown()` and native backend readiness rather than the visibility at queue time. Hide/suspend does not reset the fit factor. Recreated webviews receive zoom on their next positive page report. I did not establish native race freedom or test render-process crashes.

## Size / split recommendation

PR 9's 101 changed lines / 2 files are already a coherent unit. PR 10's **222 changed lines / 6 files** are also reviewable in size; the host/panel/solver changes form one scaling contract. Keep the WebView2 guard, startup minimum update, and macOS exclusions with the zoom feature. Removing them just to shrink the diff would reintroduce known mismatches.

A split is optional, not a merge gate: first camera aspect-width fitting and fullscreen/first-frame triggers in `StatusPanel.{cpp,hpp}`; then AMS zoom plus its four host/panel files and the solver extension, based on the first change. Both layers need screenshot provenance and standalone validation. Do not split into tiny per-platform patches that leave an invalid intermediate host/zoom contract. Prefer fixing ASTRA-CAM-001 and shortening the body over manufacturing a larger stack. The mathematical solver comment is useful maintenance context; deleting it is not a substantive simplification.

## Checks performed and limits

- `git diff --check BASE HEAD` passed for PR 9 and PR 10. Exact numstats, body counts, source-identity checks, and backend diffs are saved in `checks.json`.
- wx text/backend sources were unchanged old-upstream → new-upstream except the inspected Edge change. Combined-wx → new-upstream also differs in the expected proposed GTK label patch; `checks.json` deliberately records that nonzero diff result. It does not change the inspected borderless-text sizing code.
- Ran only the focused Python resize model (nine cases). An initial fixture mistakenly used height 324 while expecting the 574-width clamp; the assertion exposed the fixture error. The final fixture uses the source's actual 288 minimum and passes. No native test or compilation was performed.
- Earlier camera/temperature reports were inspected, but their executable models were not rerun or counted as fresh validation.
- Exploratory commands had one unquoted zsh glob error and one nonexistent `Bridge.ts` lookup; corrected source reads used `Bridge.tsx` and explicit paths. Neither changed files or supplied finding evidence.
- Screenshots were checked as attached links/provenance in the frozen bodies, not opened or regenerated. Their older combined-build origin remains. The newest Linux integration artifact was not launched; Windows/macOS have not been compiled/run here; current CI absence is not independently classified as a regression.

The parent should verify ASTRA-CAM-001 against the exact source and can return a correction or rebuttal in a fresh round. This report does not start round 2 and makes no all-OS or merge-readiness certification.
