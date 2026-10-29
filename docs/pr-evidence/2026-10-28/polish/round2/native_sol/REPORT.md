# Round 2 — native Sol review

**Open blockers: 0. New findings: 0. Prior NSOL-001: resolved.** No remaining objection in this partition; stop after this round.

## Scope and exact inputs

Read code at immutable Git SHAs, not working-tree source. Focused semantic review covered app PRs 1, 2, 5, 6, 7, 8, progress, and GTK adoption. wx-02 was inspected for the adoption/default-off boundary. All sixteen descriptions, patch statistics, parents, commit counts, evidence references and integration composition were checked. Other product areas remain with their assigned reviewers.

| Candidate | Exact base | Exact head | Review |
|---|---|---|---|
| bambu-01 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `f4218e246f3041077177d2487ce8824d522addfa` | focused |
| bambu-02 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `3ba2657c70ef031d011da175a4daafb850e3b3b1` | focused |
| bambu-03 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `ed5e975a59ee28242f67ded5e0722b19b61e0ed4` | metadata/body only |
| bambu-04 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `44fa2692b16919f4519595d6bcd4f571777ea1d6` | metadata/body only |
| bambu-05 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `305b41867feec57eb3d535d59920a9f091991762` | focused |
| bambu-06 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `2604e8279cf03f0ac93b53205608a7d901aacfc4` | focused |
| bambu-07 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `9df1217e47951f34cd95c65159f5329c88083c75` | focused |
| bambu-08 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `5d431fccc52f0011f0613a74d224e81bc614d23f` | focused |
| bambu-09 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `fc074b0ad0a55945fefcf16fe0b195a48d20e398` | metadata/body only |
| bambu-10 | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7` | metadata/body only |
| bambu-project-startup | `79df7ae309be398ed30c9f397c13c9911c2edc57` | `a2edccd9347f53d719984fd2997ce23155ee79a6` | metadata/body only |
| bambu-progress | `305b41867feec57eb3d535d59920a9f091991762` | `5608a478ca983cc63083627bb6f8854f575412db` | focused |
| bambu-ams-zoom | `bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7` | `54083d6fb80138c3404a58abc2c4300c0035dfd7` | metadata/body only |
| bambu-gtk-integration | `5608a478ca983cc63083627bb6f8854f575412db` | `e77253cd2ff240df00890d2e798faa312df23e95` | focused |
| wx-01 | `abb542694ef4534a50e65c5b877b2774d02952ae` | `14a14a773c74ae23281417f58334b5c28ecfed12` | metadata/body only |
| wx-02 | `abb542694ef4534a50e65c5b877b2774d02952ae` | `d54f3313028fc439cea91f0b6a213e5ad2245b90` | adoption boundary only |

App combined: `e9617d1a815183350bd9822fb894996aa086f47a`. wx integration: `0f2037facedf3d92660e7071b6754fe994aa744d`, on upstream `abb542694ef4534a50e65c5b877b2774d02952ae`. Public evidence read from exact commit `9ea10ea751a655b1c964f08ac4b2ce95bef07622`, at `docs/pr-evidence/2026-10-28/polish/README.md`.

## Prior finding and parent response

**NSOL-001 — non-blocking, resolved.** I accept the split after checking the source independently. `bambu-05` now contains unit/measurement fixes (66+/63−, 18 files). `bambu-progress` contains progress behavior (9+/10−, two files). Its parent is the units head. GTK adoption has the progress head as its parent, with a separate startup opt-in and exact wx pin.

The old mixed head `a1b43d73c23d08db6aa19047286c47c51f4cbe38` and new progress head `5608a478ca983cc63083627bb6f8854f575412db` have the same full Git tree, `d714d9dedd6bfca70f9f58f1bd98a3864421c9d4`. `git diff` between them is empty. This verifies the split without relying on the parent’s script or summary. The progress description separately discloses the persistent scrollbar and unbreakable-word limit. No further split or framework is requested.

## Source conclusions

- **Assembly 1:** the exact final blob matches the prior reviewed head. `_exit_assembly_to_3d_view()` posts `EVT_GLVIEWTOOLBAR_3D`; `Plater.cpp:12485–12486` still calls `leave_assemble_stack()` then `view3D->reload_scene(true)`. Removing the earlier reload preserves the queued refresh path. No newly demonstrated cross-port failure.
- **Assembly 2:** now independent on master. The only source difference from its prior stacked head is the omitted PR1 change; the sidebar/panel edits are retained. `get_collapse_toolbar_height()` returns zero for Sidebar::None, and the new panel/Return coordinates use existing canvas scale conventions. The baseline fixed panel width/narrow-window limit is not a new regression.
- **DPI 5:** reviewed changed calls and the existing bitmap/Button/SideButton helpers. `create_scaled_bitmap()` already converts its nominal size with `FromDIP()`; Button and SideButton forward their icon size through ScalableBitmap. Measured text/window extents remain native coordinates, fixed spacings remain DIPs, and point font sizes stay points. This supports the arithmetic rationale; it does not prove native Windows/macOS rendering.
- **Progress:** inspected exact `ProgressDialog.cpp:84–127, 194–209, 263–276, 818–822`. The split keeps viewport conversion, FitInside, scrollbar allocation, initial formatting before Fit, and wxDialog size dispatch together. No additional behavior was introduced by the split.
- **Print Options 6:** the exact difference from `cbde5d...` moves the helper’s layout call to the two user selection paths (`PrintOptionsDialog.cpp:213,221`). The status path still updates the description at line 804 and refreshes once at line 862. Snapshot visibility changes are followed by that same enclosing refresh. The existing Label auto-wrap uses size events and rewraps on SetLabel. No uncovered current caller or duplicate helper refresh remains.
- **Settings 7 / sidebar 8:** final changed product blobs equal their previous heads, and I reread their patches and relevant layout code. Field expansion retains compound/side-widget/full-width exclusions, a width cap, and reset-button reserve; sidebar changes use the existing sizers and DIP conventions. No demonstrated new regression found. Runtime coverage remains limited to the disclosed historical panels.
- **GTK adoption boundary:** `GUI_App.cpp:2909–2912` guards SetOption with GTK3 and wxUSE_SYSTEM_OPTIONS and places it before on_init_inner. The exact wx-02 source returns identity before touching GTK unless the option equals 1; the actual disabled-options header supplies GetOptionInt’s zero stub. The pinned integration contains only the five recomposed wx candidate paths relative to its stated upstream base. The temporary fork pin and native OS limits are disclosed. Comprehensive wx semantics belong to the primary wx reviewers.

## Descriptions and size

I read all sixteen candidate bodies. They are concise, describe the user-visible change, retain at least two screenshot attachments apiece, and label the images as earlier combined Linux evidence. Camera-only text explicitly says its after image also includes AMS zoom. Native OS limits and the review-fork pin are retained where material. I found no concrete description or size blocker.

All sixteen source commits have the declared base as their sole parent. The largest patch is 415 added/deleted lines; none approaches the user’s 1000-line concern. These are verified sizes, not a promise that every PR is ready to merge.

## Commands and results

- `python audit.py`: 16/16 parent, one-commit and `git diff --check` checks pass; all 14 provided app patches equal SHA-derived `git diff --full-index --binary` output. Exact patch/body hashes and old-head product-path comparisons are in `audit-results.json`.
- `python verify_boundaries.py`: source patches applied entirely in memory, with full old-context matching and no context fuzz. All 175 app hunks recompose all 43 changed paths byte-for-byte to `e9617d1a...`; all six wx hunks recompose all five changed paths to `0f2037fa...`. Path sets also match, excluding omitted or extra integration paths.
- All 33 screenshot references resolve to nonempty PNG Git blobs at their cited immutable image commit. Each of the sixteen evidence anchors exists, names the candidate head, and has a body provenance caption. Public HTTP reachability was not independently tested.
- `git show`, `git grep`, `git diff` and local exact-source snapshots supported the semantic checks above. No compiler or native application was invoked.
- Read the existing warm-build REPORT, verification JSON and parent bundle check. They name this exact pair, record native archive probes and the separate disabled-system-options build, and disclose six local CMake adaptations. I did not rerun them or turn those records into full Studio/isolated-PR acceptance.

Scripts use Python’s standard library and read-only Git. They write only into this assigned directory and do not alter repositories, indices, objects or branches. They establish input/source composition, not native behavior. An initial scratch composition assertion encountered two identical contexts; the script now uses the exact declared hunk coordinate only when that file still equals its candidate base, and its final run passes.

## Limitations

- Source review focused on bambu-01, bambu-02, bambu-05, bambu-06, bambu-07, bambu-08, bambu-progress and bambu-gtk-integration. wx-02 was read only to assess the app adoption/default-off boundary; no duplicate comprehensive wx review is claimed.
- All sixteen candidates received exact-head metadata/patch consistency, recomposition and description checks. The other seven candidates did not receive a fresh comprehensive semantic code review from this reviewer.
- No builds, compiler invocations, GUI actions, application launches, printer/profile operations, GitHub writes, branch/index edits or child delegations were performed.
- No Windows/macOS build or runtime validation. No native GTK/Wayland/GLX runtime or asynchronous event-loop settling tests in this round.
- The independent scripts check source and input consistency only; in-memory patch application, Git object availability and PNG signatures do not prove rendering, public URL availability or native behavior.
- Existing Linux warm-build/probe records were inspected, not rerun. They disclose six local CMake adaptations and hidden/no-frame harness limits; they do not establish isolated-PR or full Studio runtime acceptance.
- Historical screenshots remain evidence from earlier combined Linux builds. Translations, monitor migration, narrow dialogs, other printer/settings panels and long unbreakable progress strings are not newly established by this review.
- The temporary review-fork wx pin must be replaced with an accepted revision before upstream submission as already disclosed. No upstream submission or all-OS/merge-readiness claim is made.

No new fixes requested. Return to the parent for verification; do not start another review round.
