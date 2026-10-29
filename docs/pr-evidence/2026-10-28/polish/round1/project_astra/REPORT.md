# PR 3 and PR 4 adversarial review — round 1

**Open blocking findings: 1 (PA-001).** No repository, index, branch, application, GUI, profile, printer or GitHub state was changed. All output is under this directory. No delegation, compiler, build, native application or browser was started.

## Exact inputs

- App base: `79df7ae309be398ed30c9f397c13c9911c2edc57`.
- PR 3: `0826d59e1e1b36bf80b82904859c64f339749820`, 291 additions / 164 deletions across five files.
- PR 4: `b3dacfa61b17385703e700779207e83e0c1041af`, 32 additions across two files.
- Integration app: `1f880d3cd36e0317ff6535a7a089a30f079a4042`. Its seven relevant files are byte-identical to their respective PR heads (`git diff` produced no output).
- wx backend/event sources: `e2fa9bda52f720242e35def30ac4a01fbe75f5a8`. The five inspected backend/event files are unchanged in combined wx `3fea0af433d9630f79eaf8fbfc062364ba456be3`. Also inspected their delta to new upstream `abb542694ef4534a50e65c5b877b2774d02952ae`: only `webview_edge.cpp` changes, adding ten lines in `UpdateBounds` to set rasterization scale. That delta does not change bridge registration or script dispatch. It is not a Windows rendering verification.
- Frozen PR descriptions: `/tmp/bambu-polish-20261028/live-prs.json`.

Sources were read with `git show <SHA>:<path>`, `git grep <SHA>`, and `git diff <base> <head>`. Copies and hashes are in `sources/` and `source-checks.json`. Historical findings were consulted after independent source inspection.

## PA-001 — blocking — early metadata replay loses a successful model-link lookup

**New finding; introduced by PR 3.** Location: `src/slic3r/GUI/Project.cpp:308–313` and `resources/web/model_new/index.js:24–32,39–47,158–166` at PR 3's exact head.

Concrete sequence:

1. `index.js` has loaded, but DOM ready has not fired. Local metadata with an empty `model_id` arrives. `HandleStudio` stores it in `pendingProjectMessage`.
2. The optional HTTP request completes successfully before DOM ready. The new targeted native script sets `m_ModelID = "123"`; the title may not exist yet. It does not update the buffered payload.
3. DOM ready replays that older payload. `ShowModelInfo` assigns its empty ID back to `m_ModelID` and removes the title's link class.
4. The replay also sets `projectInfoReceived = true`, so the startup handshake is skipped. The native cache has the valid ID, but this document does not ask for it again. The link remains unavailable until another reload/navigation.

This is a concrete missed successful optional update, not a claim of lost metadata or editor data. macOS is an eligible initial-load path because `dispatch_project_payload` deliberately bypasses the bridge-ready gate under `__APPLE__` (`Project.cpp:125–135`). App `WebView::RunScript` uses asynchronous WKWebView evaluation (`Widgets/WebView.cpp:1195–1198`, `Utils/MacDarkMode.mm:107–114`). `index.html:17–18` loads another script after `index.js`, allowing a document to have the handler without being DOM-ready. The reader explicitly supports this early-push state. Other ports' initial bridge gate narrows this schedule; no native reproduction or frequency estimate is claimed for any OS.

**Reproduction:** `node check-reader.cjs` executes the exact complete reader JS and reconstructs the exact native link-update JavaScript from the C++ string literals, substituting ID `123`. The pre-DOM sequence yields ID `123` before DOM ready, ID `""` afterwards, no `link` class and zero handshake requests. The ordinary DOM-ready-first control retains the link. See `reader-results.json` and `extracted-model-link.js`.

**Smallest practical fix:** when applying a successful link update, also copy the resolved ID into an existing buffered `show_3mf_info` payload, checking that its nested model object exists. Preserve the native generation/lifetime/project guards and the editor exclusion. No full payload replay is needed. `proposed-model-link.js` is a scratch-only candidate with that additional assignment; the same schedule then retains ID `123` and the link. Routing this through the existing `3mf_detail_set_modelid` handler is also reasonable, but is a somewhat larger edit than fixing the current targeted script.

**Verification needed:** rerun the failing schedule against freshly extracted fixed sources, plus DOM-ready-first, missing/clear buffered message, navigation/new-document, editor-open and failed-HTTP cases. A native delayed-document-load check would establish backend timing, but missing native access is not the reason for this finding. The supplied test proves the state transition under an explicitly injected schedule; it does not prove a native race frequency or a complete fix across all schedules.

## Lifecycle, worker and HTTP review

No additional supported blocker found in these paths:

- `Project.cpp:187–245` snapshots Model/configuration on the UI thread. Worker inputs own their strings/JSON. `Reload` is static; its map at line 960 is local, despite its member-like name. The old deep Model copy and worker-side app/config access are removed.
- `Project.cpp:85–116` serializes alive/generation checks with the destructor and posting. The queued UI callback checks again before using captured `this`. The mutex is released before invoking a callback that can itself post through the same gate. wx's actual `QueueEvent` locks its pending queue (`src/common/event.cpp:1272–1309`), and `ProcessPendingEvents` removes an event before invoking it (`1321–1394`). This supports the intended handoff, not a proof of every app shutdown/reentrant event schedule.
- Generation protects reload/clear/destruction, while `matches_project` also compares live auxiliary-root and design identity (`118–123`, calls at `264`, `289`, `300`). The new accessor returns the exact existing `backup_path + "//Auxiliaries"` spelling without creating files (`Model.cpp:1094–1103,1187–1189`); this also preserves a Windows-style root string. It is not a Windows filesystem/Unicode test.
- Model remains the cleanup owner: `Model::set_backup_path` and `load_from` retire/transfer the backup tree (`1201–1220`), with whole-root deletion in `bbs_3mf.cpp:9558–9567`. Normal archive/new-project transitions use `load_from` (`Plater.cpp:9577,20271`), and close clears the backup path (`22777,22815`). Removing duplicate Project deletion is justified. Owner cleanup still uses its existing UI task path; this PR does not make recursive cleanup universally nonblocking or solve arbitrary retired-path reuse.
- Local publication is queued before starting the optional HTTP worker (`Project.cpp:259–277`). Actual `Http.cpp:455–467` calls completion only for 2xx. Its cancellation hook propagates a progress callback's flag (`232–245`); timeout setters use libcurl's second-based connect/total options (`280–287`). Stale completions still pass through the gate. This is cooperative cancellation, not immediate thread joining.
- Only positive parsed IDs enter the cache; failed/empty lookup results are deliberately retried on later visits. Cache remains on UI. Country-scoped cache keys were not added, but the original cache was already keyed by design ID; no new demonstrated country-switch defect is asserted.
- The HTTP completion mutates only the cached ID and reader link and skips `is_editing_page()` (`Project.cpp:299–315`). It no longer replays all metadata into the editor. Existing editor `HandleStudio` overwrites form contents when a full `show_3mf_info` arrives (`js/editor.js:748–755`), so retaining this exclusion is necessary. Unchanged save/dirty-query raw-this callbacks and broader editor reload behavior are outside the new lifetime guard's guarantee.
- Unchecked `wxStat` and initial reload-thread construction without a catch already occur in the base. They are not regressions introduced here. No guard should be removed to reduce the diff.

## Browser compatibility evidence

The `window.wx.postMessage` check matches each actual backend alias:

- GTK: wx `src/gtk/webview_webkit2.cpp:1321–1366` registers the handler, installs `window.wx = window.webkit.messageHandlers.wx` for future documents, and runs it on the current document. App registration is deferred via `CallAfter` (`Widgets/WebView.cpp:1051–1096`).
- macOS: wx `src/osx/webview_webkit.mm:552–604` installs the same alias with current/future document paths. App subclass/registration behavior is shared infrastructure, not changed by this PR. The Project push uses the asynchronous app wrapper, not wx's synchronous `RunScriptSync` wait loop.
- Windows: wx `src/msw/webview_edge.cpp:437–474,894–944` stores the requested handler until backend settings exist, aliases `window.wx` to `window.chrome.webview`, and installs document-start scripts. App sending checks the native backend and uses `ExecuteScript` (`Widgets/WebView.cpp:1188–1198`).

Fresh isolated JS checks verify eight requests over a nominal 15,850 ms without a host response, zero requests while the bridge is absent, a bridge becoming available during the retry window, early payload buffering, and normal link update. Timer throttling, bridge arrival after the bounded retry window and native renderer recovery remain limits. No native Windows/macOS build or runtime check was performed.

## PR 4 scope, contrast and layout

No new blocking finding. The selectors affect reader IDs, not editor help `.comment` elements; `editor.html` uses `css/editor.css`, and its field IDs differ. Table height override changes `figure.table` in the two reader descriptions only. Heading leading changes to a relative value without changing font sizes; natural table width, paragraph leading and image cap remain unchanged. The empty-caption selectors match elements the reader empties with `.text("")`.

The previously acknowledged inline-background limitation remains real: a white table cell with inherited text gets the new `#B3B3B5` foreground, reducing calculated contrast from about 6.69:1 to 2.09:1. Plain text on the dark page improves from about 2.31:1 to 7.39:1. These are color arithmetic from exact CSS, not rendered measurements. Imported explicit colors and backgrounds survive the existing reader sanitizer. Historical PF-09 and the frozen PR body already disclose this narrowed scope; I am not presenting it as a new discovery or requiring an unplanned rich-text color policy in this review. Preserve that disclosure. Any future correction should keep explicit background/foreground pairs coherent in reader-only display without rewriting saved markup; a universal descendant color override is not a safe fix.

Existing fixed page minimum width, unusually wide imported tables and inline important heights are not solved by this patch. No claim of responsive layout or all imported markup being readable is warranted. Existing native table-flow observations are historical combined-build evidence, not this review's rendering result.

## Size, grouping and descriptions

PR 3 is 455 changed lines, not a 1,000-plus-line patch. Most churn is replacement of the old monolithic worker, not a new general framework. Keeping local publication, copied input, lifecycle checks, identity checks and optional lookup together is defensible: splitting publication from its required safeguards would create unsafe intermediate behavior. A safe independent extraction is the reader handshake/buffering change, after PA-001's update contract is accounted for; it could be a first commit or separate small PR. I prefer two focused commits within the current PR (reader readiness; native local-first publication plus safeguards) rather than adding stack overhead solely to reduce the headline count. Keep PR 4 independent: it touches disjoint CSS files and needs neither metadata nor native DPI changes.

The frozen bodies are about 221/222 whitespace-delimited words, so they are not grossly oversized. They do read like accumulated review logs. Shorten PR 3's implementation paragraph to the user-visible behavior and one sentence that obsolete results are discarded. Keep one validation paragraph with the evidence link and platform limits. PR 4 need not include the exact AT-SPI coordinates or border-rounding tolerance in the main description; retain those in its linked evidence. Both repeat combined-build/screenshot provenance: consolidate to one caption stating screenshots show an earlier combined Linux build and predate follow-ups. Keep both screenshot links, the inline-color limitation for PR 4, and the upstream-approval restriction. Do not imply the unlaunched integration build was exercised or that CI passed.

## Checks and evidence boundaries

- Both exact `git diff --check <base> <head>` checks returned no output; `--numstat` matched the frozen totals.
- Fresh `node check-reader.cjs`: eight checks passed, including an assertion of PA-001's broken state and a scratch-only proposed-fix control. An initial syntax error in this newly written harness was corrected before the successful run; it was not an application failure.
- Four historical candidate harness source SHA256 values independently match PR 3's extracted blobs (`source-checks.json`). A first provenance command lacked a copied Model.hpp; it was extracted from the exact SHA and the completed check passed.
- Inspected historical `harnesses/project/{check.py,extract.py,tests.cpp,doubles.hpp,panel-declarations.hpp}` and recorded `project-final/{inputs.json,results.json}`. Their negative control is **intermediate PR head `a667512789236ea21f5530bcd31c496b4db43fab`, not upstream base `79df7ae…`**. The recorded four candidate cases passed ASan/UBSan, but no C++ harness was compiled or rerun here.
- That harness substitutes `boost::thread`, wx dispatcher, HTTP, filesystem adapter, backup cleanup queue, GUI/configuration and encoding. Its RunScript stores strings instead of executing JavaScript. The A-B-A test switches still-owned Models before draining workers, and `lifecycle` tests Model cleanup ownership, not concurrent ProjectPanel destruction. It does not cover PA-001, real HTTP/DNS cancellation timing, native event ordering, browser script execution, images, non-ASCII paths or real-thread teardown. Sanitizers on deterministic doubles cannot establish race freedom.
- The fresh Node harness uses actual reader code, but jQuery/DOM, scheduling and HTTP success are doubles; it does not measure layout, native latency or interprocess timing. `proposed-model-link.js` is review evidence only, not an applied source fix.

The parent should verify PA-001 and carry it into a fresh review of any actual fix. No source or body fix has been applied by this reviewer; this round stops here.
