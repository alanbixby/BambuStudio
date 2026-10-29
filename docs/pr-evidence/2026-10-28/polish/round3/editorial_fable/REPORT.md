# Editorial review, round 3 (final): editorial_fable

**Open blocking: 0.** Open non-blocking: 3 (ED-23, ED-24, ED-25). ED-15 conceded with a recorded disagreement. ED-16 to ED-22 closed. Round cap reached; no further round started.

## Reviewed heads

| key | head | base |
|---|---|---|
| bambu-01 | f4218e246f3041077177d2487ce8824d522addfa | 79df7ae3 |
| bambu-02 | 3ba2657c70ef031d011da175a4daafb850e3b3b1 | 79df7ae3 |
| bambu-03 | ed5e975a59ee28242f67ded5e0722b19b61e0ed4 | 79df7ae3 |
| bambu-04 | 44fa2692b16919f4519595d6bcd4f571777ea1d6 | 79df7ae3 |
| bambu-05 | 305b41867feec57eb3d535d59920a9f091991762 | 79df7ae3 |
| bambu-06 | 2604e8279cf03f0ac93b53205608a7d901aacfc4 | 79df7ae3 |
| bambu-07 | 9df1217e47951f34cd95c65159f5329c88083c75 | 79df7ae3 |
| bambu-08 | 5d431fccc52f0011f0613a74d224e81bc614d23f | 79df7ae3 |
| bambu-09 | fc074b0ad0a55945fefcf16fe0b195a48d20e398 | 79df7ae3 |
| bambu-10 | bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7 | 79df7ae3 |
| bambu-project-startup | a2edccd9347f53d719984fd2997ce23155ee79a6 | 79df7ae3 |
| bambu-progress | 5608a478ca983cc63083627bb6f8854f575412db | 305b4186 |
| bambu-ams-zoom | a273fd21b1580662221037549e09bd7e10bcc615 (new) | bed9f5a1 |
| bambu-gtk-integration | 74a75752f34633a5bb00d8a96bc6a30fc9a2744a (new) | 5608a478 |
| wx-01 | 14a14a773c74ae23281417f58334b5c28ecfed12 | abb54269 |
| wx-02 | d54f3313028fc439cea91f0b6a213e5ad2245b90 | abb54269 |

App combined e9617d1a; wx integration 0f2037fa (merge of 14a14a77 and d54f3313, tree equals c7cdfa5b, reachable at alanbixby/wxWidgets review/font-dpi-integration). Bodies: bodies-round3/*.md. Evidence commit 9ea10ea7.

## Round 2 findings and the parent's responses

| ID | Status | Note |
|---|---|---|
| ED-15 fork wording in wx doc | **Conceded**, disagreement recorded | The line is still in interface/wx/window.h at d54f3313. The rebuttal holds for the stated target: bambulab/wxWidgets is a fork, the option is fork-specific, and the sentence scopes the promise accurately. The PR body is clean and sysopt.h is neutral. If the patch ever goes to wxWidgets/wxWidgets, that one line should say "Under wxGTK3". No action now. |
| ED-16 camera images | Resolved | camera-columns-before/after (1376x208) viewed: before has the feed across most of the row, after has a narrower feed and a wider Control column. Captions match. |
| ED-17 process vocabulary | Resolved | Grep below returns nothing. Small residue in ED-24. |
| ED-18 wx provenance | Resolved | Both wx bodies name Bambu Studio and Linux. |
| ED-19 progress stacking | Resolved | Sentence present; master applicability stated. |
| ED-20 six sentences | Resolved | Each replacement re-read against its diff (see claim checks). |
| ED-21 shared sidebar pair | Resolved | "Original sidebar" / "Sidebar with this whole series applied", BambuStudio #8 named, no DPI number. Both images viewed. This also covers Opus DS-R3-01. |
| ED-22 fork pin | Resolved (known condition) | Body states the pin and the replacement condition. |

All round 1 findings (ED-01 to ED-14) stay resolved as recorded in round 2.

## New findings

**ED-23 (non-blocking, new in round 3).** The evidence README at 9ea10ea7 still describes the round 2 heads for the two moved PRs: bambu-ams-zoom as 54083d6f (183+/12-) and bambu-gtk-integration as e77253cd (7+/2-, 2 files). Its patches/ directory holds those round 2 diffs; the published ams-zoom patch still has the DeviceWebHost.cpp comment hunk the PR no longer carries. The round 3 candidates are a273fd21 (181+/10-) and 74a75752 (9+/4-, 3 files). Fix: republish the README and the two patch files as one new immutable commit and update the two Validation notes links, or add one sentence to those two bodies saying the notes predate a comment-only move.

**ED-24 (non-blocking, low).** Residual wording: alt text "Directly loaded Project gallery" and "Historical Control and AMS"; "probes" in bambu-progress and wx-01; "the native loading change" in project-startup does not name bambu-03; bambu-10 says the after image "includes AMS zoom" though AMS is outside the crop. Suggested plain replacements are in findings.json.

**ED-25 (non-blocking, low).** bambu-03's late-link script references `pendingProjectMessage`, which only the project-startup page script defines (master index.js has no such symbol). The reference is typeof-guarded so bambu-03 works alone, but its body never mentions the companion change, while project-startup's body does mention bambu-03. One clause fixes it.

## Claim checks against the diffs (all by exact SHA)

- bambu-01: reload_scene(true) removed from _exit_assembly_to_3d_view with a comment that the posted view switch reloads Prepare. Matches the body.
- bambu-02: panel_y = max(17*sc, collapse_toolbar_bottom_y + 6*sc); Return toolbar y follows the panel top. Matches.
- bambu-03: generation/alive checks ignore stale results; failed lookups are not cached so the next visit retries; late result runs a title-link script only when !is_editing_page(). Matches, see ED-25.
- bambu-04: dark text/link colors, figure.table height auto, heading line-height 1.25, empty captions hidden. Matches.
- bambu-05: FromDIP removed around ScalableBitmap/create_scaled_bitmap/Button sizes and already measured sizes; version font 16 pt. Matches "icon helpers that scale their own inputs" and "keep font point sizes in points".
- bambu-06: fixed 480/460 DIP widths removed, LB_AUTO_WRAP labels, level lists set to Body_12, layout_options() with a re-entrancy guard replacing scattered Layout() calls. Matches.
- bambu-07: single-option rows only, width clamped to base..base+def_width, reserve for reset button, compound rows skipped. Matches.
- bambu-08: bed panel proportion 1, wiki icon pinned to the corner on size, text_padding 2*FromDIP(6), 12 DIP spacers removed in favour of a left border. Matches.
- bambu-09: wxTE_RIGHT, targetSize("000") while editing, GetSizeFromTextSize plus MSW margin, slash anchored to the target. Matches.
- bambu-10: refit on wxEVT_SIZE, EVT_MEDIA_CTRL_FIRST_FRAME and close_camera_fullscreen; target reset to default when the row is narrow. Matches.
- bambu-project-startup: delays 100..8000 ms sum 15.85 s; pending message held until DOM ready; bridge checked before posting. Matches.
- bambu-progress: SetMaxSize removed on percent labels, ClientToWindowSize viewport, wxALWAYS_SHOW_SB, FormatString before Layout/Fit, wxDialog::DoSetSize. Matches.
- bambu-ams-zoom: max_ams_zoom 2.0, 5% steps, `#ifndef __WXOSX__` keeps AMS at zoom 1 on macOS, zoom applied only when GetNativeBackend() exists (Edge async). Matches.
- bambu-gtk-integration: GIT_TAG 0f2037fa, option set in OnInit under `__WXGTK3__ && wxUSE_SYSTEM_OPTIONS`, the two-line comment now lives here. Matches.
- wx-01: hunk sits inside `#ifdef __WXGTK3__` (control.cpp lines 341-359 at abb54269) and under `#ifndef __WXGTK4__`; only non-wrapping GtkLabel. Matches "GTK3-only and excludes GTK4".
- wx-02: option default 0 returns identity; inline FromDIP/ToDIP kept for every port except GTK3; option name equals the one GUI_App.cpp sets. Matches "default unchanged" and "Windows, macOS and GTK2 conversion code is unchanged".

## Commands run (read-only)

```
# one commit, parent == base, subject == title, tree and paths (python over curated-prs-round3.json)
git -C bambu-studio-upstream rev-list --count <base>..<head>; git rev-parse <head>^; git log -1 --format=%s/%b <head>
git -C bambu-wx-upstream rev-list --count abb54269..{14a14a77,d54f3313}
git diff 54083d6f a273fd21; git diff e77253cd 74a75752   # two comment lines only
git show 79df7ae3:src/slic3r/GUI/DeviceWeb/DeviceWebHost.cpp | grep -n -A6 'm_last_logical_content_size = wxSize(width, height)'
git show e9617d1a:... (same grep)                            # combined carries the gtk-integration wording
git diff <base> <head> for each of the 16 candidates (claim checks above)
git show 79df7ae3:resources/web/model_new/index.js | grep -c pendingProjectMessage   # 0
git -C bambu-wx-upstream ls-remote https://github.com/alanbixby/wxWidgets review/font-dpi-integration   # 0f2037fa
grep -n -i -E 'cleaned|accepted|reviewed|review fork|combined series|preload|elf|hash|quota|model|opus|sol|fable|astra|codex|claude|swarm|peer|harness|draft|approval' bodies-round3/*.md  # no process hits
grep -h -o -E 'https://[^) ]+' bodies-round3/*.md | sort -u   # 42 URLs, all HEAD 200 (url-check-round3.txt)
comm against round2/editorial_fable/urls-round2.txt            # +camera-columns-before/after, +BambuStudio pull/8, nothing dropped
curl raw README at 9ea10ea7 (evidence-README-9ea10ea7.md); 16 anchors present
curl patches/bambu-ams-zoom.patch and bambu-gtk-integration.patch at 9ea10ea7 (published-patches/)  # round 2 content, see ED-23
```

Scratch files in this directory: findings.json, urls-round3.txt, url-check-round3.txt, evidence-README-9ea10ea7.md, published-patches/, images/ (six downloaded screenshots for caption checks).

## Limitations

- Source and text review only. No build, launch, screenshots, or Windows/macOS compile or run. The warm Linux build record was not re-run.
- The evidence README was read over HTTPS; its two stale entries are ED-23.
- Word counts here (49 to 99 per body, provenance sentence and link text included) use a different measure from the root's and are not a finding.
- No all-OS or merge-readiness claim. Isolated per-PR screenshots remain missing for bambu-05, wx-02, gtk-integration, bambu-03 and project-startup, as their bodies say.
- No repositories, branches, GitHub state, GUI, or installed application were changed. No delegation. No round 4 started.
