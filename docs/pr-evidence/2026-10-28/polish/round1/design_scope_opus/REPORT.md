# Round 1 — design, scope and taste review (Opus 5.5)

**Open blocking findings: 0.** There are 12 non-blocking findings in `findings.json` (DS-R1-01 … DS-R1-12). Nothing here is demonstrably wrong or unsafe. The findings cover how the PRs are split, two visible design costs, and some cleanup.

## Reviewed heads (exact)

App base is `79df7ae309be398ed30c9f397c13c9911c2edc57`. wx base is `e2fa9bda52f7…`, and wx master is now `abb542694ef4…`.

| PR | Head | Changed lines | Verdict |
|---|---|---:|---|
| bambu#1 Assembly GL context | `f899b75e113c…` | 4 | Keep as is |
| bambu#2 Assembly sidebar clearance | `dc097952b7f6…` (on #1) | 12 | Keep; **unstack** (DS-R1-06) |
| bambu#3 Project metadata | `0826d59e1e1b…` | 455 | **Split** JS / native (DS-R1-01); 2 small cleanups (11, 12) |
| bambu#4 Project reader styles | `b3dacfa61b17…` | 32 | Keep as is |
| bambu#5 DPI double scaling | `a1b43d73c23d…` | 148 | **Split** mechanical / progress (DS-R1-04); scrollbar look (DS-R1-05) |
| bambu#6 Print Options wrap | `cbde5d139ced…` | 137 | Keep; squash; optional relayout trim (DS-R1-08) |
| bambu#7 Settings field width | `763edb4f6015…` | 65 | Keep; title understates scope (DS-R1-07) |
| bambu#8 Sidebar cards / purge | `e9658ac6a8bb…` | 29 | Keep as is |
| bambu#9 Temperature alignment | `e51f9b9c4aa1…` | 101 | Keep as is |
| bambu#10 Camera / AMS | `fab83eef842e…` | 222 | **Split** camera fit / AMS zoom (DS-R1-02); zoom cap (DS-R1-03) |
| wx#1 GTK label font | `888eaac66223…` | 24 | Keep; rebase to `abb54269` (DS-R1-10) |
| wx#2 GTK3 DIP scale | `ed8b87d0aa56…` | 84 | Keep; rebase to `abb54269`; merge gate unchanged |

All 10 app patches in `round1/*.patch` match `git diff --full-index <base> <head>` byte for byte.

## Answers to the brief

**Is each PR one reviewer-sized change?** #1, #2, #4, #6, #7, #8 and #9 each do one thing. Three PRs bundle independent changes:

- **#3 (455 lines): split it.** This is not about size. The PR fixes two separate bugs with separate triggers, and its own first sentence says so.
  - One is page-side: `index.js` retries the startup request. It is 43 lines and uses only the existing message protocol.
  - The other is native: show local metadata before the network lookup, with safe worker lifetimes. It is 412 lines.
  - Each fix works without the other. If the user wants fewer PRs, use one PR with two commits instead.
- **#10 (222 lines): split it as a stack.** This is also not about size. The camera aspect fit is plain sizer code that works the same on every OS, and macOS already runs this PR with AMS zoom fixed at 1. The AMS zoom part carries all the web-view backend risk (async WebView2, the macOS exclusion, base-zoom capture, the initial-height constant) and a debatable design. With a split, upstream can take the camera fit even if it rejects the zoom. Estimates: #10a is about 55 lines, #10b about 165.
- **#5: split mechanical from behavioral.** 17 of the 19 files repeat one mechanical unit fix that a reviewer can scan quickly. The progress dialog and progress-label changes are visible layout behavior, and they are what the PR's only screenshot shows.

**Does any cleanup add behavior or machinery it doesn't need?** No new framework or generic API remains. Two items only add diff noise: the `url_encode` swap in #3 (DS-R1-12) and the hand-copied path format in the new Model accessor (DS-R1-11). Complexity I checked and defend:

- **#3:** the generation/alive gate. A worker must not race panel or app teardown.
- **#6:** two-pass layout with `LB_AUTO_WRAP`, an existing idiom with 62 uses in base.
- **#7:** three update entry points, each one needed. The rescale order checks out.
- **#8:** the absolutely positioned help icon. It copies the printer card's 4/14 DIP corner without consuming the bed card's centred layout.
- **#9:** the text-change relayout. StatusPanel calls `GetTextCtrl()->SetValue()` directly (StatusPanel.cpp:2549-2561).
- **#10:** the per-item width loop.

The details are in `defended_complexity`.

**UI design calls (my area):**

- **#6:** Wrapping to the row width looks right. Body_12 on the selectors matches their Body_12 "Pausing Sensitivity:" labels; the stock ComboBox default is Body_14.
- **#7:** In the sidebar screenshots, field edges stay aligned and the +8 em cap is sensible.
- **#8:** Equal-width printer and plate cards fix the truncated "Text…" plate name. The help icon now matches the printer card's corner. One trade-off: long custom printer names now truncate sooner, which is acceptable.
- **#9:** The right-aligned compact current / target / unit group follows the user's no-gap reference. Slashes do not line up across rows; that comes with the design and is fine.
- **#10: two type scales in one column.** At zoom about 1.7, AMS text renders about 1.6–1.7× the native Control text next to it (DS-R1-03). I recommend capping zoom at 1.25 and naming the cap once. The user accepted the current look live, so this is their call.
- **#5: always-visible scrollbar.** `wxALWAYS_SHOW_SB` puts a permanent empty scrollbar in adaptive progress dialogs (DS-R1-05). Reserving the scrollbar width is the cleaner look. Prior reviews chose the always-visible bar for predictable geometry, so this is also the user's call.

**Other-OS concerns (from the design side only):**

- The #10 Windows check must use wx `abb54269` or later. That commit changes WebView2 rasterization scale on the same control (DS-R1-10).
- #8's unmanaged icon stays clear of the rounded corner on every platform.
- #6 drops `Fit()` on a DPI change. That is fine because the dialog has a fixed size. Still worth one check when dragging between Windows monitors with different scaling.

None of these were run on Windows or macOS.

## Recommended final grouping

There are 15 drafts. All are independent on master except #10b, which stacks on #10a.

1. #1 Assembly GL context
2. #2 Assembly sidebar clearance, rebased onto master
3. #3a Project page startup retry
4. #3b Show local Project information before the online lookup
5. #4 Project reader dark styles
6. #5a Stop double-scaling DPI-adjusted sizes
7. #5b Let print progress text use its natural height
8. #6 Print Options wrap
9. #7 Settings field width, retitled
10. #8 Sidebar cards and purge alignment
11. #9 Temperature alignment
12. #10a Fit the camera to its video aspect ratio
13. #10b Scale AMS to fill the Control column, stacked on #10a
14. wx#1, rebased onto `abb54269`
15. wx#2, rebased onto `abb54269`

Squash every PR to one plain-language commit (DS-R1-09). If the user prefers fewer PRs, keep #3, #5 and #10 whole but give each two logical commits. The largest PR after the split is #3b, at about 412 lines.

**Title ideas (Fable owns the prose):**

- #3a: "Retry the Project page's startup request"
- #3b: "Show local Project information before the online model lookup"
- #5a: "Stop double-scaling DPI-adjusted sizes"
- #5b: "Let print progress text use its natural height"
- #7: "Let single-option settings fields use spare panel width"
- #10a: "Fit the live camera to its video aspect ratio"
- #10b: "Scale the AMS panel to fill the Control column"

One prose note for Fable: every body repeats the same internal-process paragraphs (ELF hashes, "screenshots predate…", the review-evidence links). Those belong in one tracking note, not in the upstream descriptions.

## Commands run (all read-only on the repos)

- `git diff --full-index <base> <head> | diff -q - roundN/bambu-XX.patch` for all 10 app PRs → all match.
- `git log`, `git show <sha>:<path>`, `git grep` at exact SHAs: base and head code for PrintOptionsDialog, Label, GUI_Utils (DPI handling), OG_CustomCtrl, OptionsGroup, Plater, TempInput, StatusPanel, DeviceWebHost, Project, Model, ProgressDialog, GUI_App::url_encode, and the wx gtk/window.cpp and msw/webview_edge.cpp commit `60b64f83b2`.
- PR2 unstack check: copied the 3 master files into scratch and ran `patch -p1 --dry-run < bambu-02.patch`. Every hunk applies (offset −2), rc=0. Afterwards I deleted the scratch copy.
- Screenshots: read the published PNGs from fork commit `91aa62a0` with `git show` into `img/`, plus the local `settings-field-width-{before,after}.png`.
- Size estimates for the splits come from `git diff --numstat` per file. The #10a and #10b numbers are estimates; nothing was implemented.

## Limitations

- I had no GUI access and did not build or run anything. No Windows or macOS run. The design calls rest on source plus historical combined-build Linux screenshots, which do not show the isolated PR heads.
- I implemented none of the proposed splits. The #10a/#10b and #3a/#3b line counts are estimates. The parent must build each split before relying on it.
- **The combined branch changed during this review, and not by me.** `cleanup/combined` advanced from `1f880d3c` to `b7a37924`, with commits at 20:21 and 20:25:
  - `0b34fcad4` touches Project.cpp (+3).
  - `b7a379241` touches StatusPanel.cpp (+4/−1).

  Both are outside the frozen heads I reviewed. They touch the same areas as #3 and #10, so round 2 should look at them. The wx repo HEAD is unchanged at `3fea0af4`.
- I made no claims about all-OS behavior or merge readiness.
