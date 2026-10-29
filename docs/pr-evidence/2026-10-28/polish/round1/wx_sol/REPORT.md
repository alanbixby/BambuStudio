# wx1/wx2 and upstream integration — Sol, round 1

**Open blocking findings: 1, limited to dependency integration/rollout. Open non-blocking findings: 1, description accuracy. No new wx implementation defect established.** No repository, index, branch, installed application, profile, printer or GUI was changed. No network, delegation, build or native probe was used. All writes are under this assigned output directory.

## Exact inputs

| Item | Exact SHA |
|---|---|
| wx1 head | `888eaac6622399a7b226f96fab837940c5cd5dc1` |
| wx2 head | `ed8b87d0aa56d9d6e703e617df5e446f85d3ffd4` |
| Frozen wx base | `e2fa9bda52f720242e35def30ac4a01fbe75f5a8` |
| Current wx upstream | `abb542694ef4534a50e65c5b877b2774d02952ae` |
| wx combined | `3fea0af433d9630f79eaf8fbfc062364ba456be3` |
| Bambu upstream/base | `79df7ae309be398ed30c9f397c13c9911c2edc57` |
| Bambu #5 consumer corrections | `a1b43d73c23d08db6aa19047286c47c51f4cbe38` |
| Bambu combined | `1f880d3cd36e0317ff6535a7a089a30f079a4042` |
| Local release/20260417 snapshot | `b506005bc4ee62124e24bf00e0f58656db3646a6` |
| Local release/20260929 snapshot | `f5e51a20bd328d4a043af9344825d7347270c2c9` |

The two patches were regenerated from exact objects and matched the frozen patches byte for byte. Changed wx blobs also match the combined wx head. Live bodies were read from the frozen JSON, not fetched. Historical round-one/two wx reports were read for context after inspecting the source; their conclusions were not treated as fresh verification.

## WXSOL-001 — blocking integration gap

The current Bambu recipe still selects `https://github.com/bambulab/wxWidgets`, `GIT_TAG master` at `1f880d3:deps/wxWidgets/wxWidgets.cmake:27–28`. `deps/CMakeLists.txt:155` forwards the unparsed Git arguments into ExternalProject_Add. No integration pin is present in that combined head or isolated #5. Today a fresh default dependency fetch therefore omits the fork GTK fixes. After wx2 reaches upstream master, the same recipe exposes old consumers to the new conversion.

Both locally available release snapshots also use `GIT_TAG master`. Their Linux scripts select GTK3 (`b506005:BuildLinux.sh:155`, `f5e51a2:BuildLinux.sh:164`). The newer release retains the old measured-width expression at `f5e51a2:src/slic3r/GUI/MediaPlayCtrl.cpp:1115`:

`FromDIP(GetSize().GetWidth() - 120 - measured label width - measured button width)`.

wx2 makes that conversion nonidentity at fractional font DPI (`ed8b87d:src/gtk/window.cpp:4391–4457`). App #5 correctly confines conversion to the nominal constant at `a1b43d7:src/slic3r/GUI/MediaPlayCtrl.cpp:1117`. As an arithmetic illustration, with window width 1000, measured children 100/20 and font scale 1.5, the old release permits status width `min(1140,900)=900`; the corrected expression permits `min(700,900)=700`. This proves a unit mismatch without claiming a fresh native clipping result. The floating recipe is baseline behavior; wx2 activates the additional GTK failure. It is not an independent new Windows/macOS defect.

The existing body warnings accurately describe a gate, but do not implement dependency selection or protect release recipes. The old review accepted the warning as closing its documentation finding. This review does not reinterpret that as an implementation fix: the present partition explicitly asks for a usable integration plan.

**Decision: a separate, small Bambu dependency-pin/integration PR is needed** for a reproducible default build of the reviewed pair. It should contain the exact wx repository/SHA selection and a short source-pair/build note. Keep it separate from the 19-file consumer cleanup in #5. No dependency framework or new API is needed.

A workable sequence for the parent/maintainers is:

1. Prepare a wx integration revision that includes `abb5426` plus both GTK patches. The existing combined `3fea0af` is based on `e2fa9bd` and does **not** contain the new Windows change. Pinning it directly would drop that change. Either replay the GTK commits on `abb5426`, or merge the upstream advance into the integration branch. Both patch orders were checked in scratch and preserve the reviewed GTK blobs.
2. In the fork-only Bambu draft, select that exact published integration SHA. If it exists only in `alanbixby/wxWidgets`, the declared repository must be that fork too. A SHA existing locally or only in another repository is insufficient. Preserve a clear path to replace the fork URL with the upstream URL once the identical content is reachable there. No upstream PR/submission is authorized by this review.
3. App #5 may merge before the wx semantics change. wx1 can merge independently. Before wx2 merges to shared wx master, maintainers must either backport the consumer corrections to each supported release branch or pin those branches to their last validated pre-wx2 revision. `e2fa9bd` is the frozen prior base; `abb5426` is a newer candidate that additionally needs its Windows change validated for the chosen release. Do not silently select a new dependency revision for an old release merely to satisfy the pin.
4. If maintainers cannot protect the supported release recipes, the safe alternative is an opt-in wx branch containing wx2, consumed only by corrected Bambu branches through an exact SHA. Hold wx2 off shared master. This avoids requiring uncorrected release builds to acquire the new contract.
5. For immutable historical tags, document use of an archived dependency or the one-line source pin when rebuilding. Do not rewrite tags. Local branch sampling cannot identify every fork/consumer; maintainers must define supported releases.
6. Rebuild wx and application together from the pinned pair in clean dependency/application outputs. The GTK3 conversion changes from inline identity to exported out-of-line methods: mixed old application objects or old libraries are not a sound validation setup. Record the actual pair in evidence. Only then claim that default builds reproduce the integration.

This finding blocks wx2-to-shared-master and a claim of completed reproducible integration. It does not block wx1, app #5 landing early, or unrelated application PRs. Required verification is recorded in findings.json. A paragraph promising later coordination is not the concrete pin diff requested here.

## WXSOL-002 — non-blocking scope wording

wx1's body says “Wrapped labels and other widgets retain their existing path.” At `888eaac:src/gtk/stattext.cpp:237`, wxStaticText::DoGetBestSize disables GTK line wrapping before delegating measurement at line 249, then restores wrapping at line 251. wxStaticTextBase inherits the control implementation of DoGetBestSize. Consequently a wrapped static text can reach the new unwrapped-label check at `src/gtk/control.cpp:356`.

This establishes a wording problem, not a runtime defect. Replace the sentence with: “The check runs only when GTK measures a label without wrapping; other widget types keep their existing path.” Keep the GTK4 exclusion. Do not promise exclusion of all wrapped wxStaticText controls.

## Upstream advance and applicability

Only these new exact commits are present between the frozen and current upstream bases:

- `60b64f83b2c9d23c9149cf843baaf1a83e57f85f`: disable Windows WebView2 text scaling.
- `abb542694ef4534a50e65c5b877b2774d02952ae`: merge that commit, with parents `e2fa9bd` and `60b64f8`.

The only changed file is `src/msw/webview_edge.cpp`. Its UpdateBounds now queries ICoreWebView2Controller3, disables automatic monitor-scale detection and sets rasterization scale from the native control DPI. There is no overlap or redundant portion in either GTK patch. No source edit is required merely to make them apply. Both full patches pass `git apply --check` on scratch copies of the new base, in either order; actual application to those scratch copies yields the same four touched blobs as `3fea0af`.

The new base warrants Windows integration checks for text scaling and monitor DPI, particularly for browser-based Bambu panels. It does not establish a regression in these GTK patches. The CMake SDK default remains `1.0.1418.22` (`abb5426:build/cmake/lib/webview/CMakeLists.txt:63`); no Windows compiler or runtime was used. The upstream-only diff also has existing trailing whitespace at `src/msw/webview_edge.cpp:181`; that is not a wx1/wx2 defect. No future un-fetched upstream changes were assessed.

## Implementation checks and limits

**wx1:** The addition is inside the existing GTK3 branch and excluded for GTK4. GTK2 and non-GTK source paths are unchanged. It compares the owned CSS font description with the widget Pango context, invalidates only on mismatch and frees the owned description. Hidden-state and size-request restoration remain on the surrounding path. Warning suppression follows existing macros. The settled no-repeat-invalidation argument requires GTK to bring that Pango font into agreement after invalidation; I found no new wx label style-updated callback that would itself force recursive measurement. This is source reasoning, not a fresh proof across GTK themes/releases. No leak, unconditional invalidation, or demonstrable sizing-loop defect was established.

**wx2:** GTK3 leaves the inline identity path while macOS retains it (`include/wx/window.h:2077`). Common non-DIP definitions remain guarded by `!wxHAVE_DPI_INDEPENDENT_PIXELS`, so there is no duplicate GTK3 definition. Windows/GTK2/other ports retain their previous definition path. New code uses C++98 constructs and the existing wx math header; no C++11 requirement was introduced. This is not a compiler result.

The scale is screen font DPI / 96, read per call after obtaining screen settings. Integer GDK window scale is deliberately not multiplied into wx logical coordinates. GetDPIScaleFactor/GetContentScaleFactor retain their integer-scale contract, and interface documentation explicitly records the fork divergence. Null/unrealized handles fall back to the default screen; no screen or invalid DPI falls back to identity. A live widget is still required when a nonnull window is supplied. Dynamic relayout, real XSettings normalization, distinct-monitor migration and native Wayland remain unverified.

The helper preserves -1 and zero, keeps positive inputs positive and other negatives away from the sentinel, saturates before rounding and uses inverse scaling in ToDIP. A Python transcription checked 13,398 signed/boundary cases, including direct/inverse extreme factors, plus a 96/120/144/192-by-GDK-1/2 matrix. Noninvertible rounding/saturation at tiny and extreme values is expected; the patch does not promise exact round trips. This script does not compile or execute the C++ and is not native DPI evidence.

**Threads:** FromDIP/ToDIP now touch GTK3 settings/widget state; consumers should call them on the GUI thread with live windows. A bounded lexical scan of 73 explicit thread-source files found 64 recognizable lambda bodies and no direct FromDIP/ToDIP/create_scaled_bitmap/ScalableBitmap call in those bodies. Near-line candidates in SelectMachinePop and TextureImportDialog were checked: the DIP calls belong to separate UI methods, outside worker lambdas. No direct calls were found in src/libslic3r or src/slic3r/Utils. This cannot cover indirect calls, callbacks from external APIs, macro expansion or all startup ordering. No demonstrated new off-thread call was established, so absence of a complete call graph is a limit, not a blocker. A cached mutable global scale would add complexity and stale-screen behavior without fixing an established caller defect.

## Size, descriptions and evidence

wx1 is +24/−0 in one file; wx2 is +81/−3 in three files, including the necessary declaration/documentation changes. Both are comfortably reviewable and have separate purposes; keep them separate. The frozen bodies are approximately 172 and 272 whitespace-delimited words. Their test prose is dense but does not require another blocking rewrite. Optional polish: keep problem/change, the wx2 merge gate, one validation sentence and one limits sentence; link the detailed matrix once. Preserve screenshot links and their combined-build disclosure. The only concrete incorrect scope sentence found is WXSOL-002.

The supplied latest Linux integration artifact is unlaunched and based on a separately stated app revision, with a comment-only source difference. I did not inspect/run that binary or promote it to exact-head native evidence. Existing screenshot and historical probe results do not establish independent PR or all-OS validation. There are no new native Windows/macOS results from this review.

## Checked commands/results and deliverables

`verify.py` is self-contained, uses only Python's standard library and Git reads, and writes beside itself. `python3 verify.py` passed. `commands.json` retains exact command/result records and source outputs. `verification.json` records:

- Frozen-patch byte identity and combined touched-blob identity: pass.
- Base-to-head `git diff --check` for wx1, wx2 and Bambu #5: pass.
- Both patch application orders on the new base, check and scratch-only application: pass.
- 13,398 arithmetic cases and the DPI matrix: pass within the stated model.
- Lexical worker-lambda scan: zero direct DIP/helper hits; not a thread-safety proof.
- New upstream full-diff whitespace check: exit 2 for the unrelated trailing whitespace identified above.

`findings.json` contains stable IDs, exact locations, triggers/outcomes, minimum fixes, verification needs and blocking scope. Source extracts, both scratch application trees and `upstream-advance.patch` support independent inspection. No second review round was started.
