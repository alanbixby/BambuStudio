# Astra round 2 — temperature, camera and AMS

**Open blocking objections: 0. New findings: 0.** All three prior findings are resolved within their stated scope. This partition has converged; no further review round is requested. This is not an all-OS or merge-readiness claim.

This review covers the three candidates assigned to the temperature/camera partition of the sixteen-candidate manifest. It does not certify the other thirteen candidates. No repository, index, ref, GUI, installed application, profile or printer was changed. No builds, native applications, network actions or child delegations were started. Only this scratch directory was written.

## Exact source reviewed

| Candidate | Head | Base | Changed lines |
|---|---|---|---:|
| Temperature / bambu-09 | `fc074b0ad0a55945fefcf16fe0b195a48d20e398` | `79df7ae309be398ed30c9f397c13c9911c2edc57` | 101 |
| Camera / bambu-10 | `bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7` | `79df7ae309be398ed30c9f397c13c9911c2edc57` | 49 |
| AMS / bambu-ams-zoom | `54083d6fb80138c3404a58abc2c4300c0035dfd7` | `bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7` | 195 |

Each is one commit and passes `git diff --check`. Source was read with `git show SHA:path`, not from candidate branch names or summaries. Relevant combined app source was checked at `e9617d1a815183350bd9822fb894996aa086f47a`. Inspected wx scroller, text-entry and webview sources at `abb542694ef4534a50e65c5b877b2774d02952ae` are byte-identical in integration `0f2037facedf3d92660e7071b6754fe994aa744d`.

## Prior findings and disposition

**ASTRA-CAM-001 — resolved (originally blocking).** Camera `StatusPanel.cpp:2054–2076` and AMS `StatusPanel.cpp:2124–2179` now derive the row budget from the visible client width, minus the three actual outer spacers, bounded by natural minima. Both refresh the virtual extent with `FitInside()` after changing the minimum. The old allocated-width feedback path is gone.

I verified the camera-only production source and extracted helper against the native fixture bytes. The AMS helper differs from the tested `010ae25289256dda9f0d09111cf24c28bdf44394` only by naming the existing 2× constant; a controlled normalization confirms this, and its final helper is byte-identical in the combined app. The fixture structure, synthetic controls, event pumping and raw data were inspected independently.

My scratch audit rereads 44 candidate TSV files / 440 observations (360 combined camera/AMS, 80 camera-only), verifies their corresponding recorded zero exits and JSON rows, and checks extent contraction, camera minima, necessary undersized scrolling and finite settling. Camera-only records additionally preserve the natural Control width and show zero AMS setter calls. The original compact negative-control TSV independently retains 800 px excess at 96 DPI/scale 1: client1385 versus virtual2185. Corrected records show1385/1385; undersized records retain985/1218. These are audits of supplied native results, **not fresh native executions**.

**ASTRA-CAM-002 — resolved (non-blocking evidence correction).** The published correction at immutable commit `9ea10ea751a655b1c964f08ac4b2ce95bef07622`, `docs/pr-evidence/2026-10-28/polish/corrections.md`, matches the local publication byte-for-byte. It correctly identifies the old336/344 and width-driven260→340 schedules as synthetic. I traced the actual hook (`AmsControlWebPage.tsx:23–39,119–128`), band calculation (`geometry.ts:116–141` and `dip.ts`), bridge (`DeviceWebBridge.cpp:270–279`) and host (`DeviceWebHost.cpp:603–676`) at the AMS head. The hook reports positive changed heights with fixed width586; full-body band combinations produce233/249/270/286/287/303/324/340. No resize/zoom-generated follow-up report is assumed. Pending zoom is applied before the jitter filter, so an actual initial report can apply it even when host height is unchanged. The correction properly supersedes misleading historical implications without rewriting historical reviews.

**ASTRA-DOC-001 — resolved (non-blocking editorial).** The three exact `bodies-round2` files now state behavior, checks/limits, screenshot provenance and one evidence link without the former repeated review history. The camera body explicitly says its after image includes the separate AMS change. Both original image URLs are preserved in each applicable description; none is presented as a final isolated-candidate screenshot. The operational upstream-approval constraint remains binding, without needing repetition in the PR prose. No publishing was performed.

## Compatibility and remaining limits

The camera-only split has no AMS conditional or browser calls. The AMS split deliberately leaves macOS at normal zoom; the inspected Cocoa implementation uses magnification (`src/osx/webview_webkit.mm:619–626`). The Windows native-backend guard precedes zoom access; inspected Edge initialization and accessors support that ordering (`src/msw/webview_edge.cpp:379–395,715–724,824–827`). Actual WebView2 startup/recovery and Cocoa behavior remain untested here.

Temperature source is byte-identical to round1 and to the combined app. I reread its focus, value, sizing and rendering changes, plus the native wx sizing implementations. There is no newly identified temperature regression. Windows/macOS typing, caret and click behavior still need native checks. Existing readonly keyboard/submission semantics and unchanged-height AMS DPI-refresh behavior remain baseline observations, not new candidate findings.

The three changes are small enough to review individually, and the AMS dependency is explicit. Keeping the existing 2× cap and macOS behavior is a design choice, not an unresolved defect.

I read the new integration build report and parent bundle check, but did not independently repeat that build, hash the bundle, or inspect all build inputs. Their Linux build result is separate evidence, not end-user acceptance. The inspected native fixtures use synthetic minima, fallback16:9 media and a stand-in AMS panel; they do not cover real playback, first-frame dispatch, fullscreen lifecycle, DOM rendering, arbitrary page-state schedules or all future events. No Windows/macOS build or runtime was performed. Screenshot links/provenance were checked; images were not visually reinspected or fetched.

## Reproduction and artifacts

Run `python3 -I /tmp/bambu-polish-20261028/round2/camera_temperature_astra/audit.py` to repeat the read-only source and recorded-result audit. It passed. It writes only beside itself and does not compile or launch anything. Its limits are in the script docstring and above.

`checks.json` records exact Git commands, exits, source/body comparisons, stats and raw-result assertions. `sources.json` records exact source paths, heads and SHA-256 values, with local source snapshots. `findings.json` carries the three resolved IDs and zero open blockers. No round3 has been started.
