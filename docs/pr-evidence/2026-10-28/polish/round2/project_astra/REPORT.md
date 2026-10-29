# PR 3 and PR 4 — adversarial review, round 2

**PA-001 is resolved in the local candidate. Open blocking findings: 0. New findings: 0.** This partition has converged; no third round is requested for these unchanged inputs. This is a scoped source review, not an all-OS or overall stack merge-readiness claim.

Only the assigned scratch directory was written. No source, repository, branch, index, GitHub, GUI, installed application, profile or printer was changed. No delegation, build, compiler, browser or application was started.

## Exact reviewed inputs

| Input | SHA |
|---|---|
| App base | `79df7ae309be398ed30c9f397c13c9911c2edc57` |
| PR 3 previous head / negative control | `0826d59e1e1b36bf80b82904859c64f339749820` |
| PR 3 local candidate | `c0be044cd4ab4c69f857b52354fecfca50f420b3` |
| PR 4 unchanged head | `b3dacfa61b17385703e700779207e83e0c1041af` |
| Combined candidate | `0b34fcad456618e5d023e4f475dffb3f75ae6472` |
| Pinned wx source | `e2fa9bda52f720242e35def30ac4a01fbe75f5a8` |
| Combined wx | `3fea0af433d9630f79eaf8fbfc062364ba456be3` |
| New wx upstream, supplied local object | `abb542694ef4534a50e65c5b877b2774d02952ae` |

PR 3's candidate is **unpublished** according to the brief. This approval of the PA-001 correction applies to that local SHA, not the old remote draft. No GitHub state or current upstream tip was queried this round.

Sources were freshly extracted with `git show <SHA>:<path>`, then read directly. `source-manifest.json` records exact SHA/path/copy/SHA256 values. The combined candidate has byte-identical copies of all five PR 3 paths and both PR 4 paths. Frozen bodies were read from `round1/bambu-03-body.md` and `round1/bambu-04-body.md`; no editorial candidate was supplied.

## PA-001 — blocking in round 1, resolved in this candidate

**Original trigger and outcome:** before DOM ready, local metadata with an empty model ID is buffered; a successful optional lookup updates the reader's current ID; DOM-ready replay then restores the buffered empty ID and removes the link. The reader already counts that replay as receipt of metadata, so its handshake does not retrieve the newly cached ID.

**Exact fix:** `src/slic3r/GUI/Project.cpp:311–313` at `c0be044…` copies the resolved ID into the existing `pendingProjectMessage.model.model.model_id` when the pending command is `show_3mf_info` and its nested values are present. `resources/web/model_new/index.js:24–32,39–47,158–166` then replays the corrected object. No full metadata replay is added.

The entire previous-to-candidate diff is three string-literal lines in `Project.cpp`. Removing those lines reproduces the previous file byte-for-byte (`fix-provenance.json`). The parent description of its edit is accurate.

**Fresh execution:** the original 14-check harness was copied into this scratch directory, pointed at freshly extracted exact-SHA files, and run successfully. Its source-extracted JavaScript fails the first fixed assertion with the previous PR 3 head: expected ID `123`, actual empty string. This negative control is the previous PR head, **not upstream base**. The upstream base lacks this targeted script and buffering combination.

Eight additional checks pass, for 22 checks in the extended run. They establish that the update:

- Changes only the buffered nested ID, preserving payload and nested-object identity and unrelated metadata.
- Leaves a clear-command payload unchanged even if it contains a nested model.
- Tolerates absent, null and selected primitive nested values without throwing in the targeted script.
- Adds a missing ID to a valid nested model.
- Handles clear-then-metadata and metadata-then-clear buffer replacement without changing a superseded payload.
- Remains targeted after replay and on repeated execution; unrelated rendered-description state is not overwritten.

The smallest practical fix requested in round 1 has been applied. No further source change is requested for PA-001. Native delayed-load verification could establish real backend timing and frequency, but it is not needed to confirm the demonstrated JavaScript state correction.

## Guard and regression review

The correction sits entirely inside the existing optional-success callback and `!is_editing_page()` branch (`Project.cpp:299–318`). Source inspection confirms these unchanged safeguards:

- `post_reload_result` checks alive/generation before posting and again in its UI callback (`85–116`). Clear increments the generation and empties the cache (`943–956`). A stale result rejected by those checks cannot execute the added literals.
- Live auxiliary-root/design identity is checked at publication and lookup completion (`118–123,264–265,289–290,300–301`); the completion also requires a nonempty native payload.
- Only a positive parsed ID reaches the targeted update (`296–298,330–355`). The optional worker still owns its inputs; HTTP cancellation, timeout handling and cache behavior are unchanged.
- Editor detection still checks the current URL for `editor.html` (`1102–1109`). Editor `show_3mf_info` still replaces form state (`resources/web/model_new/js/editor.js:748–757`), so keeping the native exclusion matters. The new code neither dispatches a full payload nor changes that exclusion. This is source evidence, not an exercised editor runtime.

The nested guard is a truthiness check, not complete schema validation. It is sufficient for the native JSON shape and the missing/null cases relevant here. Arbitrary objects with getters, frozen objects, hostile proxies and malformed full metadata are not promised support.

The clear-path tests deserve precise wording: they prove the pending clear message is not converted into metadata and the reader blanks the tested fields. They **do not prove the reader resets its global model ID or removes every link class**. `ShowProjectInfo(null)` at `index.js:121–131` does not reset those, and that behavior is unchanged from the exact upstream base. Injecting a successful link script after a clear also bypasses the native generation gate; this synthetic schedule tests command guarding, not real stale-completion rejection. No new blocker follows from this inherited behavior.

Likewise, the parent harness's “failed lookup” case simply omits the success script; it does not execute HTTP failure, timeout or cancellation. Its “new document” case creates a separate VM and does not simulate a native navigation race. The “latest buffered metadata” case uses compatible synthetic messages and does not validate native project identity. Those limits remain explicit.

## Cross-OS and unchanged PR 4

The three new literals use ordinary JavaScript property reads/writes, `typeof`, `var` and existing string comparison idioms. They add no platform API, native header, ABI or path conversion. Exact candidate app sources still route Windows script dispatch through WebView2 `ExecuteScript` (`Widgets/WebView.cpp:1188–1194`), macOS through asynchronous WKWebView evaluation (`1195–1198`, `Utils/MacDarkMode.mm:107–114`), and Linux through WebKitGTK below that branch. No backend was exercised.

Read-only diffs of the five previously reviewed wx browser/event files show no change between pinned and combined wx. Their delta to supplied new upstream is still only the `UpdateBounds` rasterization-scale change in `src/msw/webview_edge.cpp`; it does not alter the reviewed bridge/event mechanism. These diffs do not establish whole-wx compatibility or render behavior.

PR 4 remains an independent 32-added-line CSS patch. Re-reading its exact diff and complete styles shows no new issue. Description-heading leading and table-height overrides remain scoped to the two reader descriptions; caption selectors target the three reader IDs; editor help styling is not broadened.

The known inline-color/background limitation remains: inheriting `#B3B3B5` inside an explicit light-background table cell can reduce contrast. `resources/web/model_new/css/dark.css:159–166` changes the inherited foreground; the sanitizer still retains inline styles (`index.js:152–155,253–256`). This is the previously disclosed PF-09 limitation, not a new finding or a claimed fix. It stays visible in the frozen PR 4 body. No new rendering measurement was made.

## Reviewability and checks

PR 3 is now **294 additions / 164 deletions = 458 changed lines across five files**; PR 4 is **32 additions across two files**. No 1,000-plus-line PR is introduced in this partition. The focused three-line correction needs no new API, generic framework or extra split. Keep native publication and its safety checks together; keep CSS independent. Prior prose advice remains: consolidate duplicate screenshot provenance, move test-coordinate detail into linked evidence, and keep platform/inline-color limits and the upstream-approval boundary. No revised body has been reviewed or published by this reviewer.

Reproducible commands run in this directory:

- `node check-parent.cjs` — 14 checks pass using freshly extracted candidate sources.
- `node check-reader.cjs` — 22 checks pass (includes those same 14, not 36 distinct checks).
- `node negative-control/check-parent.cjs /tmp/bambu-polish-20261028/round2/project_astra/sources/previous__src__slic3r__GUI__Project.cpp` — expected exit 1 on the original replay assertion.
- `git diff --check <base> <candidate/PR4-head>` — both exit 0, no output.
- `git diff --numstat <base> <candidate/PR4-head>` — sizes above.
- `git diff <candidate/PR4-head> <combined-candidate> -- <respective paths>` — no output.
- `git diff <pinned-wx> <combined-wx/new-upstream> -- <five browser/event paths>` — exact outputs in `wx-checks.json` and companion patches.

Logs/results: `test-runs.json`, `parent-results.json`, `candidate-results.json`, `negative-control.log`, `git-checks.json`, `fix-provenance.json`, `source-manifest.json`.

**Verification limits:** Node VM executes the actual reader and reconstructed native-script literals, but DOM/jQuery, timers and success scheduling are doubles. No real renderer, network, native event ordering, threads, teardown stress, editor runtime, Windows/macOS compile/run, C++ compilation or native build was performed. No CI result was obtained. Historical Linux screenshots/builds are not this candidate's runtime evidence. These limits do not independently establish a regression.
