# Editorial / maintainer-path review, round 1 (editorial_fable)

Open blocking count: **1** (ED-01, editorial only: the live bodies are not upstream-ready as written). It is resolved by applying `proposed-bodies/*.md`; no source change is needed. Thirteen non-blocking findings, of which four need a decision from the parent (ED-10 squash, ED-11 optional PR5 split, ED-07 and ED-04 need native confirmation of a sentence each).

## Answers to the user's three questions, from this partition's view

- **Too verbose / AI-slopified?** Yes. Live bodies run 125 to 315 prose words, 3 to 4 of their paragraphs are the same four disclaimers pasted into every PR, and most state the screenshot-provenance fact twice. They also carry internal process language (ELF hash, "no-preload build", "peer-review follow-ups", "Fork draft only; upstream submission requires approval"). The proposed bodies cut this to 117 to 233 words with one provenance sentence and one evidence link each. The four longest (PR3, PR5, PR10, wx-02) stay above the 120-word target on purpose: they carry behavior changes, known limits or the wx merge gate that a maintainer must see.
- **Small enough to merge?** Yes. No PR is near 1000 lines. Largest: PR3 at 455 lines over 5 files, PR10 at 222 over 6, PR5 at 148 over 19 files. PR5 is the one legitimate split candidate (ED-11), and only for reviewer focus, not size.
- **Other OSes?** Not this partition's call on correctness. Editorially, every proposed body states once that Windows and macOS were not built or run, and names the platform-specific behavior the diff contains (PR5 Windows above 100%, PR8 Windows button rectangle, PR9 Windows/macOS text allowances, PR10 macOS AMS stays unzoomed, wx-02 GTK3 only). The wx-02 merge gate remains explicit and is cross-referenced from PR5.

## Reviewed heads

| Key | Repo | Head | Base | Lines (+/-) | Files | Commits |
|---|---|---|---|---|---|---|
| bambu-01 | BambuStudio #1 | f899b75e113c4e7fdf422842c4403e9b62906bdd | 79df7ae3 (master) | 3/1 | 1 | 1 |
| bambu-02 | BambuStudio #2 | dc097952b7f667fa22a7dcf5979d73fa6b3485e4 | f899b75e (PR1) | 10/2 | 3 | 2 |
| bambu-03 | BambuStudio #3 | 0826d59e1e1b36bf80b82904859c64f339749820 | master | 291/164 | 5 | 3 |
| bambu-04 | BambuStudio #4 | b3dacfa61b17385703e700779207e83e0c1041af | master | 32/0 | 2 | 1 |
| bambu-05 | BambuStudio #5 | a1b43d73c23d08db6aa19047286c47c51f4cbe38 | master | 75/73 | 19 | 2 |
| bambu-06 | BambuStudio #6 | cbde5d139ced56b5e3d7def490446f06ccd2e791 | master | 66/71 | 2 | 3 |
| bambu-07 | BambuStudio #7 | 763edb4f601575e364ae3fa58aadf014f1ca7adf | master | 64/1 | 3 | 2 |
| bambu-08 | BambuStudio #8 | e9658ac6a8bbcffe38eeb6eb0cce0d446e3c672f | master | 21/8 | 1 | 1 |
| bambu-09 | BambuStudio #9 | e51f9b9c4aa1489fcf73e3a9dc0b7e454cd8db37 | master | 80/21 | 2 | 2 |
| bambu-10 | BambuStudio #10 | fab83eef842e6967fa06d0bb05410940b4787d28 | master | 219/3 | 6 | 3 |
| wx-01 | wxWidgets #1 | 888eaac6622399a7b226f96fab837940c5cd5dc1 | e2fa9bda | 24/0 | 1 | 2 |
| wx-02 | wxWidgets #2 | ed8b87d0aa56d9d6e703e617df5e446f85d3ffd4 | e2fa9bda | 81/3 | 3 | 2 |

All twelve diffs were read in full from `round1/*.patch`; facts used in the proposed bodies were checked against source at the exact heads (see commands).

## Deliverables in this directory

- `proposed-bodies/{bambu-01..10,wx-01..02}.md`: complete replacement bodies. Every screenshot URL from the live bodies is preserved byte-for-byte (25 images, verified by `check_bodies.py`). Each body keeps exactly one evidence link (the per-PR `peer-review/` tree link already in the live body; PR10 keeps its newer 9abf504f link). PR5 and wx-02 additionally keep their companion-PR links.
- `titles.json`: proposed titles for all twelve, each also the suggested squashed commit subject. All under 72 characters.
- `findings.json`: fourteen findings, ED-01 to ED-14.
- `body-check.json`, `check_bodies.py`: word counts and URL-preservation check (text only; fetches nothing).
- `urls.txt`: the 29 distinct URLs in the live bodies, all HTTP 200 at review time.

## What the proposed bodies change, and what they deliberately drop

Kept: the visible problem first, what changed, one testing sentence with honest classification, the material OS note, the merge gate (wx-02, echoed in PR5), the known limits a maintainer needs (PR3 retry-on-visit, PR4 inline cell colors, PR5 always-visible scrollbar and growing percent row, PR10 settling passes, PR9 Windows/macOS gaps), all screenshots with their captions, provenance ("earlier combined Linux build of this whole series, app commit 53fdfb6, not this branch alone"; for wx: "Bambu Studio built with this change and its companion fixes").

Dropped: the four repeated disclaimers; the ELF hash (the app commit from `validation-native.json` carries the provenance); the "Fork draft only; upstream submission requires approval" sentence (that is an instruction to the operator; GitHub's draft flag and the user's binding rule carry it); the `validation-native.json` link (it sits one directory above the kept evidence tree link, at `docs/pr-evidence/2026-10-28/`); PR10's `STATUS.md` link (ED-02); the "Independent of #5" notes (base is master); harness counts in prose (ED-03). If the parent wants the validation record linked directly, add it as a second link; nothing else in the bodies depends on it.

Word counts, live vs proposed (prose only, images and link targets excluded): 01 199→123, 02 125→117, 03 213→184, 04 207→151, 05 315→229, 06 156→141, 07 137→141, 08 158→153, 09 176→163, 10 265→218, wx-01 164→148, wx-02 266→233. PR7 grew by four words because the live body omitted the eligibility rule and the refresh triggers, which a reviewer of that diff will ask about.

## Findings (details and evidence in findings.json)

- **ED-01 blocking, all 12.** Bodies not upstream-ready: repeated boilerplate, duplicated provenance, process language. Fix: apply proposed bodies.
- **ED-02, PR10.** Linked `STATUS.md` opens by naming a review model and an API rate limit. Fix: link dropped.
- **ED-03, PR1/4/5/10/wx-02.** Measurement soup in prose. Fix: plain testing sentences.
- **ED-04, PR5.** Body opens with the merge gate although PR5 is the safe-first side. Fix: lead with the defect; one ordering sentence.
- **ED-05, PR2/4/8/10.** Fork-number and swarm-internal cross references. Fix: title reference for PR2, drop the rest, renumber at submission.
- **ED-06, PR2/6/7/8.** Testing claims that are not tests. These four have Linux combined-build screenshots only. Fix: say so.
- **ED-07, PR6.** Removal of the fixed 480 DIP column width is not mentioned; validation record notes no narrow/wide check. Fix: one sentence; native reviewer should confirm what now governs the width.
- **ED-08, PR5.** Always-visible progress-dialog scrollbar and growing percent row were asides. Fix: explicit sentences.
- **ED-09, titles.** Mechanism-first titles. Fix: `titles.json`.
- **ED-10, history, 9 PRs.** Duplicate-subject commits, PR6 add-then-remove, PR10 comment-only commit, wx "Address peer review for <branch>" commits. Fix: squash to one commit per PR with the proposed title; PR2 rebased on squashed PR1. Non-blocking only because GitHub squash-merge would hide it; I did not verify upstream BambuStudio's merge style, so if they merge without squashing this history lands.
- **ED-11, size.** None over 1000 lines. Optional PR5 split into mechanical (17 files) and behavioral (3 files) halves for reviewer focus. PR3 should stay whole.
- **ED-12, wx-01/02.** Base e2fa9bda is behind upstream abb54269; merge-tree clean, touched files unchanged upstream. No action.
- **ED-13, wx-02.** Branch-comparison link replaced by the PR5 link.
- **ED-14, PR3.** "Bounded" handshake quantified: about 16 s.

## Checked commands and results

```
# frozen bodies equal live JSON; prose counts; diff sizes
python3 -I (inline)          -> body_matches_disk=True for all 12
# commit subjects/bodies per PR (bash, word-split)
git -C bambu-studio-upstream log --format='%h %s' <base>..<head>   (all 10)
git -C bambu-wx-upstream log --format='%h %s' e2fa9bda..<head>      (both)
# merge checks
git merge-tree --write-tree 79df7ae3 <head>   -> clean for all 10 app heads
git merge-tree --write-tree abb54269 <wx-head> -> clean for both wx heads
git diff --name-only e2fa9bda abb54269 | grep -F -f <wx touched files> -> none
# facts used in bodies
git show 763edb4f:src/slic3r/GUI/Field.cpp        -> def_width()=8, def_width_wider()=12
git show dc097952:src/slic3r/GUI/GLCanvas3D.cpp   -> get_collapse_toolbar_height() returns 0 when sidebar docking state is None
grep -c '^-.*FromDIP' bambu-05.patch              -> 53 removed lines; ICON_SINGLE_SIZE 12; 19 files
grep in bambu-05.patch                            -> timeout_connect(3).timeout_max(8) in PR3; wxALWAYS_SHOW_SB in PR5
bambu-03.patch index.js                           -> retry delays 100+250+500+1000+2000+4000+8000 ms = 15.85 s
# links
curl -o /dev/null -w %{http_code} -L <29 URLs>    -> all 200
curl https://github.com/alanbixby/BambuStudio/pull/5 -> 200
validation-native.json                            -> reviewed_app_commit 53fdfb67, elf 88df689c, labels_checked 31, resize_attempt ignored
STATUS.md (camera-review)                         -> first sentence names a model and a rate limit
python3 -I editorial_fable/check_bodies.py        -> ALL_IMAGES_PRESERVED; no model/quota/process words
```

Repositories were read only (`git status --short` clean in both; HEADs 1f880d3c and 3fea0af4 unchanged). Nothing was written outside this directory. No push, PR, comment, build or GUI action.

## Limitations

- This is an editorial review. I did not compile, run, or assess code correctness; sentences in the proposed bodies that describe behavior were checked against the diffs and the cited evidence files, not against a running build. Two sentences need a native reviewer's confirmation before publication: PR6 "the dialog's own size sets it" (ED-07) and PR5 "safe to merge on its own" against stock wx (ED-04).
- Word targets: four bodies exceed 120 prose words by design; the parent may trim the "Known limits" sentences if a shorter body is preferred, but each dropped limit is a documented behavior.
- Upstream BambuStudio and wxWidgets merge conventions (squash vs merge commit) were not verified; ED-10's severity assumes the parent squashes before submission as already planned.
- Screenshot provenance was taken from `validation-native.json` (app commit 53fdfb67). I did not re-derive which exact binary produced each PNG.
- No all-OS or merge-readiness claim is made here beyond "merge-tree clean against the declared bases and the current upstream masters".
- Shared checkout drift, not caused by this review: `bambu-studio-upstream` HEAD (branch `cleanup/combined`) was 1f880d3c when I started and b7a37924 when I finished (two new commits at 20:25 local: "Preserve an early model link when Project metadata is replayed", "Refit the Device columns to the visible client width"; 7 lines in Project.cpp and StatusPanel.cpp). I ran only read commands (`log`, `show`, `diff`, `status`, `merge-tree --write-tree`). All my reads were by the frozen PR head SHAs, which are separate refs and unchanged, so nothing above is affected. If those two commits become new PR3/PR10 heads, the proposed bodies for PR3 and PR10 should be re-checked against them in round 2.
