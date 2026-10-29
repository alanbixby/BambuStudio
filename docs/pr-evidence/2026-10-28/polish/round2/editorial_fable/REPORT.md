# Editorial / maintainer-path review, round 2 (editorial_fable)

Open blocking count: **0**. All fourteen round-1 findings are resolved or conceded (table below). Eight new non-blocking items, ED-15 to ED-22. One of them (ED-15) is a one-line documentation string inside the wx-02 commit that should be amended before any upstream wx submission; the rest are caption and sentence wording on the fork drafts. No blocking objection remains, so this partition stops after this round.

## Answers to the user's three questions, from this partition

- **Too verbose / AI-slopified?** No longer. The sixteen bodies run 54 to 79 prose words (median 72). Each has: what changed, one testing sentence that names what was actually run, one untested-OS sentence, the screenshots, one provenance sentence, one evidence link. No model, quota, hash, draft or approval language remains. Some captions still carry internal words ("Cleaned", "native", "combined series", "accepted"); see ED-17.
- **Small enough to merge?** Yes. All sixteen are single commits whose subject equals the PR title. Largest is bambu-03 at 415 changed lines over 4 files; next are bambu-ams-zoom (195 over 6) and bambu-06 (138 over 2). Nine PRs are under 70 lines. The three splits done since round 1 (Project native vs page script, camera fit vs AMS zoom, DPI units vs progress layout) recompose exactly; bambu-05 + bambu-progress reproduce the old PR5 tree byte for byte.
- **Other OSes?** Not this partition's call on correctness. Editorially, every body now states once what was not run (Windows/macOS for all app PRs; other wx ports for wx-01/02), and the platform-specific statements in the bodies match the diffs: bambu-05's Windows-only effect, ams-zoom's macOS-unzoomed and Windows-backend-wait, wx-02's GTK3-only default-off option, wx-01's GTK3 block (verified: the hunk sits inside `#ifdef __WXGTK3__` in src/gtk/control.cpp at 14a14a77). The default-off wx option plus the separate pinned-adoption PR replaces the round-1 merge-gate prose, which is a clearer story for a maintainer.

## Reviewed heads (all read by exact SHA; one commit each; parent == declared base; title == commit subject)

| Key | Head | Base | +/- | Files | merge-tree vs upstream master |
|---|---|---|---|---|---|
| bambu-01 | f4218e24 | master 79df7ae3 | 3/1 | 1 | clean |
| bambu-02 | 3ba2657c | master | 10/2 | 3 | clean (destacked from PR1; `get_collapse_toolbar_height` exists on master) |
| bambu-03 | ed5e975a | master | 254/161 | 4 | clean |
| bambu-04 | 44fa2692 | master | 32/0 | 2 | clean |
| bambu-05 | 305b4186 | master | 66/63 | 18 | clean |
| bambu-06 | 2604e827 | master | 67/71 | 2 | clean |
| bambu-07 | 9df1217e | master | 64/1 | 3 | clean |
| bambu-08 | 5d431fcc | master | 21/8 | 1 | clean |
| bambu-09 | fc074b0a | master | 80/21 | 2 | clean |
| bambu-10 | bed9f5a1 | master | 49/0 | 2 | clean |
| bambu-project-startup | a2edccd9 | master | 40/3 | 1 | clean |
| bambu-progress | 5608a478 | bambu-05 305b4186 | 9/10 | 2 | clean; progress-only diff also applies to master |
| bambu-ams-zoom | 54083d6f | bambu-10 bed9f5a1 | 183/12 | 6 | clean |
| bambu-gtk-integration | e77253cd | bambu-progress 5608a478 | 7/2 | 2 | clean |
| wx-01 | 14a14a77 | abb54269 | 24/0 | 1 | clean |
| wx-02 | d54f3313 | abb54269 | 91/3 | 4 | clean |

wx integration 0f2037fa is a merge of exactly wx-01 and wx-02 on abb54269 and has the same tree (db3c30ee) as c7cdfa5b. Evidence commit 9ea10ea7 README matches the local `publication/README.md` byte for byte and carries explicit `<a id="key">` anchors, so every `#bambu-xx` link lands on its section.

## Round-1 findings: disposition

| ID | Status | Basis |
|---|---|---|
| ED-01 | resolved | Bodies rewritten; all 23 screenshot URLs preserved (bambu-05's two progress images moved to bambu-progress with the split). |
| ED-02 | resolved | No STATUS.md link; immutable evidence commit. |
| ED-03 | resolved | No raw counts in prose. |
| ED-04 | resolved | bambu-05 split; no gate paragraph; Windows effect stated. |
| ED-05 | resolved | No fork numbers; stacked bodies describe their base (except bambu-progress, ED-19). |
| ED-06 | resolved | "Checked visually on Linux" for 02/06/07/08; harness claims only where a harness exists (checked against publication/README.md and implementation/). |
| ED-07 | resolved | Body says the inner column follows the dialog width; the dialog still sets 480x520 DIP (PrintOptionsDialog.cpp:33 at 2604e827); narrow-dialog behavior named as untested. |
| ED-08 | resolved | bambu-progress states the always-allocated scrollbar and the growing percent row. |
| ED-09 | resolved; wx prefix conceded | Titles are the commit subjects. "wxGTK3:" prefix is a style choice for wx maintainers; conceded. |
| ED-10 | resolved | All 16 single commits, no commit bodies; bambu-02 on master. |
| ED-11 | resolved | `git diff a1b43d73 5608a478` is empty. |
| ED-12 | resolved | Both wx heads on abb54269. |
| ED-13 | resolved | No branch-comparison links. |
| ED-14 | resolved | "about 16 seconds" (delays sum to 15.85 s). |

Parent's response to each accepted as stated; I found no case where the response claimed something the candidates do not do.

## New findings (details, evidence and fixes in findings.json)

- **ED-15, wx-02 (fix before upstream).** `interface/wx/window.h` doc text says "In this wxGTK3 fork, ...". Replace with "Under wxGTK3, ...". One-line amend.
- **ED-16, bambu-10.** The camera PR's images show no camera (cropped for privacy) and the after image is dominated by the stacked AMS zoom. The same evidence commit has `camera-columns-before/after.png`, which show the camera band next to the Control column and make the width change visible. Use those for bambu-10.
- **ED-17, captions and words.** "Cleaned ...", "Combined native geometry", "Directly loaded native ...", "Unclipped native progress", "Native heading", "the combined series", "the accepted 2x limit", "reviewed revision / review fork / accepted wx revision". Replace with Before/After captions and plain words.
- **ED-18, wx-01/02.** "Images show an earlier combined Linux build of this series" means nothing in the wxWidgets repo; say "Images show Bambu Studio on Linux built with this change and its companion application fixes."
- **ED-19, bambu-progress.** Body does not say it is stacked on the DPI PR, nor that it applies to master alone (it does).
- **ED-20, six sentences.** bambu-03 editor sentence over-promises live update; bambu-progress "unbreakable filenames" opaque and the `wxDialog::DoSetSize` change unmentioned; bambu-08 "the pill" undefined; gtk-integration "older applications" is a wx statement in an app PR; bambu-02 "remains pinned in place" unclear; bambu-10 opening sentence hard to parse. Replacements given.
- **ED-21, bambu-05 / gtk-integration / wx-02.** Shared sidebar pair: for bambu-05 it shows none of the touched surfaces; for the other two it does show the font-DPI effect but the captions do not say what to look at, and the crops are different sizes.
- **ED-22, gtk-integration (known limit).** Pin targets the personal fork; cannot go upstream until bambulab/wxWidgets carries wx-01/02. Body says so. No action now.

## Checked commands and results

```
python3 -I (inline) over curated-prs.json:
  git log -1 --format=%P/%T/%s/%b <head>      -> parent==base, tree==declared, subject==title, body empty, all 16
  git rev-list --count <base>..<head>          -> 1 for all 16
  git diff --name-only/--shortstat base..head  -> files and +/- equal curated-prs.json, all 16
  git merge-tree --write-tree <upstream master> <head> -> rc=0 for all 16
git log -1 --format=%H %T %P 0f2037fa / c7cdfa5b     -> same tree db3c30ee; 0f2037fa parents = wx-01 head + wx-02 head
git rev-list --count abb54269..0f2037fa            -> 3
git grep get_collapse_toolbar_height 79df7ae3      -> defined in GLCanvas3D.cpp:2705 / .hpp:1022
git diff --stat a1b43d73 5608a478                  -> empty (bambu-05 + bambu-progress == old PR5)
git archive 79df7ae3 StatusPanel.cpp ProgressDialog.cpp | git apply --check <progress-only diff> -> applies
git show 2604e827:PrintOptionsDialog.cpp | grep SetSize -> line 33 SetSize(FromDIP(480),FromDIP(520))
git show e77253cd:GUI_App.cpp | grep sysopt        -> line 59 #include <wx/sysopt.h>
git show 14a14a77:src/gtk/control.cpp (lines 325-390) -> new block inside #ifdef __WXGTK3__, before gtk_widget_get_preferred_size
git ls-remote https://github.com/alanbixby/wxWidgets  -> 0f2037fa refs/heads/review/font-dpi-integration
curl -L -w %{http_code} <39 distinct URLs in bodies>   -> all 200 (urls-round2.txt)
curl raw README @9ea10ea7 | sha256sum vs publication/README.md -> identical; 16 <a id> anchors present
GitHub contents API docs/pr-evidence/2026-10-28 @91aa62a0 -> camera-columns-before/after.png exist; manifest says camera excluded for privacy
grep -iE 'opus|codex|...|accepted|cleaned|harness|fixture|draft|approval' bodies-round2/*.md -> hits only in ED-17 list
python3 -I image/word check -> 23 round-1 images all present in round-2; prose 54..79 words
grep -rl 'c++98' implementation/wx-opt-in -> conversion probes compiled with -std=c++98 -pedantic-errors (supports wx-02 testing sentence)
Images viewed: 18 of the 23 body screenshots plus camera-columns-before/after and camera-ams-after (images/)
```

Repositories were read only. One `git apply --check` with a mistyped option failed at argument parsing in the app checkout and changed nothing; the real check ran in a temporary directory that was removed. `git status --short` is clean in both checkouts (see end of this file). Nothing was written outside this directory. No push, PR, comment, build or GUI action.

## Limitations

- Editorial review: I did not compile or run anything. Sentences describing behavior were checked against the diffs at the exact heads and against the cited evidence files, not against a running build.
- The Windows statement in bambu-05 ("corrects oversized icons on Windows above 100% scaling") follows from stock wx making FromDIP non-identity only on MSW; it is a source argument, not a Windows run.
- The historical screenshots come from an earlier combined build (app 53fdfb67 per validation-native.json, or the v02.08.04.57 checkpoint per manifest.json); I did not re-derive which binary produced each PNG. The new e9617d1a build has no screenshots.
- Prose word counts use the same text-only method as round 1 (images and link targets excluded).
- No all-OS or merge-readiness claim is made beyond "merge-tree clean against the declared bases and the current upstream masters".
