# Cleanliness review, round 3 (cleanliness_fable)

Open blocking count: **0**. No regression found in the two heads that changed since round two. Four non-blocking items remain, all description or comment hygiene; one is new.

## Governing inputs (read by SHA, nothing modified)

- Map: `/tmp/bambu-peer-review-20261028/round3/final-heads.json`
- App base `79df7ae309be398ed30c9f397c13c9911c2edc57`, combined `47a28ade55ec26d12096151f8ad7d93ebde174bc` (tree `14e1b958…`)
- wx base `e2fa9bda52f720242e35def30ac4a01fbe75f5a8`, combined `3fea0af433d9630f79eaf8fbfc062364ba456be3` (unchanged since round two)
- Bodies: `/tmp/bambu-peer-review-20261028/round2/bodies/*.md` (mtime 02:06, PR5 02:12, PR10 02:23)
- Evidence branch `review/screenshots` in the application fork: `089bbf96` (harness payload), `4505000a` (linked from all bodies), `0c2cd4e4` (tip; STATUS.md linked from PR10). The tracking repo `bambu-studio-linux-fixes` does not contain these commits; they live in `bambu-studio-upstream`.

Reviewed heads (full SHAs in `findings.json`): bambu-1 f899b75e, bambu-2 dc097952, bambu-3 0826d59e, bambu-4 b3dacfa6, bambu-5 a1b43d73, bambu-6 **cbde5d13** (new), bambu-7 763edb4f, bambu-8 e9658ac6, bambu-9 e51f9b9c, bambu-10 **df28193c** (new), wx-1 888eaac6, wx-2 ed8b87d0. Local `fix/*` refs point at these heads; both worktrees are clean at their combined commits.

## What changed since round two, and what did not

`git diff 24d91027 47a28ade` touches exactly four files: `Widgets/ComboBox.cpp`, `Widgets/ComboBox.hpp`, `Widgets/TextInput.hpp` (all reverted to the PR base) and `DeviceWeb/DeviceWebHost.cpp` (the PR10 initial-height fallback). Nothing else moved. Ten of twelve heads are byte-identical to the round-two heads I already reviewed, so their round-two verdicts stand.

Composition was re-verified independently of `final-heads.json`: every single-owner path has the same blob at its PR head and at the combined commit; the three shared files (`Plater.cpp` PR5+PR8, `StatusPanel.cpp` PR5+PR10, `GLCanvas3D.cpp` PR1+PR2) reproduce the combined bytes when both patches are applied to the base. No combined file is outside the declared path lists. The exported `bambu-06-*.patch` and `bambu-10-*.patch` in round3 equal `git diff BASE HEAD` apart from index lines. `mergeability.json` records exit 0 for all 24 merges; upstream master is still `79df7ae3`, so "latest-upstream" and "declared-base" coincide.

## Prior findings

**CF-01 (bambu-6) — resolved by removal; conceded in full.** At `cbde5d13` the PR touches only `PrintOptionsDialog.cpp/.hpp` (66+/71-). All four `Widgets/TextInput.*` and `Widgets/ComboBox.*` blobs equal the base (`cf7e1a12`, `0fe74b46`, `e734d135`, `2d695e56`) at both the PR head and the combined commit. The five selectors are constructed with `wxCB_READONLY`; the unchanged base `ComboBox::Create` hides the entry and the unchanged `ComboBox::SetFont` (`ComboBox.cpp:199-204`) therefore reaches `wxWindow::SetFont` on the outer control, which `TextInput::render` paints with `GetFont()` (`TextInput.cpp:331`). This is the simplest correct form; my round-two "drop the Widgets hunks" recommendation is exactly what landed. I also checked the historical-screenshot claim: in the round-one build (`191c22e`) `TextInput::SetFont` additionally re-fonted the hidden entry and re-ran `messureSize`, but `messureSize` derives height from `text_ctrl->GetSize()`, which `SetFont` does not change, so the selector height in the historical captures equals what the final head produces. The PR6 body now states "All TextInput and ComboBox files retain their stock behavior", which supersedes the stale sentence print_font_sol flagged.

Residual PR6 observations, none requiring action: `update_options` calls `update_smart_nozzle_blob_mode_desc` (`:802`), which now calls `layout_options()`, and then calls `layout_options()` again at `:860`, so one redundant two-pass layout runs inside the Freeze. `on_dpi_changed` replaced `Fit()` with `layout_options()`; with the 480 min/max removed from the scrolled window, `Fit()` would have sized the dialog to the full virtual content, so the replacement is required rather than incidental. The `make_wrapped_label` comment is accurate against `Label.cpp:284-287, 345-379` (auto-wrap re-wraps on `wxEVT_SIZE`, so height is only known after the first layout).

**CF-02 (bambu-8/10) — fixed; unchanged since round two.**

**CF-03 (bambu-3/5) — fixed, pending the parent's push check.** `089bbf96` publishes the portable harnesses. `harnesses/evidence/project-final/results.json` records `after.commit = 0826d59e` (PR3 head) with the two expected baseline reds and four candidate greens; `caller-units-final/results.json` records `after.commit = a1b43d73` (PR5 head), 43 changed lines, 104 modeled cases, PASS; `historical-final/results.json` is labeled "historical fourteen-site geometry" at `e20789d7` with "PASS: 236 assertions". The README separates the 236 figure from the 43 later sites and states the eight StatusPanel/em-derived corrections are source-reviewed only, which matches the PR5 body's "51 additional" (43+8). Every body links `tree/4505000a…/peer-review/`, which contains `harnesses/` and `progress-native/`; PR10 additionally links `0c2cd4e4` for `partial-camera-review/STATUS.md`, which exists there. The remote-tracking ref `origin/review/screenshots` contains `0c2cd4e4`, which indicates a push happened, but I have no network and did not verify GitHub reachability. One wording nit: the harnesses README section "Final reviewed source runs" still says the 43-site check "is a subset of PR5", fine, but `provenance.json` still says `final_sha_runs: "Not yet possible"`; it is a frozen pre-run artifact and the README explains the later runs, so I do not count it as a defect.

**CF-04, CF-05, CF-06, CF-07, CF-09, CF-10, CF-11, CF-12, CF-13 — unchanged heads; prior statuses stand** (fixed or conceded as recorded in round two).

**CF-08 (bambu-10) — partially reopened as a residual, non-blocking.** Round two removed the literal 340 fallback; round three reintroduces it as `kAmsControlWebInitialHeightDip = 340` (`DeviceWebHost.cpp:599-600`) because the early return left the host at a different pre-report size than the panel (camera_fable scope owns that correctness argument; I accept it). What remains is a cleanliness residual: the value duplicates `kMinHeightDip = 340` in the anonymous namespace of `wgtAmsControlWebPanel.cpp:17`, and the new comment "Match the panel minimum" sits two lines above a function-local `kMinHeightDip = 220` in the same file (`:604`), so a reader following "panel minimum" can land on the wrong constant. Smallest fix: name the source in the comment, e.g. "Same value as kMinHeightDip in wgtAmsControlWebPanel.cpp; keep them equal", or pass the panel's minimum into the host at construction if the parent prefers a single definition. I do not recommend new panel state.

**CF-14 (wx-1/2) — half fixed, half open.** Both wx bodies now carry the provenance sentence. `wx-pr-2.md:12` still says the companion branch "fixes fourteen identified sites"; the parent's round-three response says no general "fourteen" total claim is retained, but the file on disk has not been updated. Replace with "corrects the original fourteen sites plus later bitmap/helper/font callers" or link the PR5 body.

**CF-15 (bambu-5) — conceded.** `Button::Create` only constructs a `ScalableBitmap` when `icon` is non-empty (`Button.cpp:54-56`), so `iconSize` is inert for the nine untouched `ICON_SINGLE_SIZE` uses, all of which pass `""`. All eleven converted sites, including the four in `SendMultiMachinePage.cpp`, pass a named icon. The PR5 body now states this rule. No further change requested.

**CF-16 (history) — retained by parent; documented disagreement, non-blocking.** Duplicate subjects remain on PR2, PR3, PR5, PR6, PR7, PR9; PR6 now also records add-then-remove of the font plumbing (`191c22e` → `8a70086` → `cbde5d1`). The parent will squash/retitle before any upstream submission, which is the point at which it matters. I accept that for fork drafts.

## New finding

**CF-17 (bambu-10 body, peer-review README) — non-blocking, description currency.** `bambu-pr-10.md:18` says "its final independent Fable recheck failed to complete due to an API rate limit" and `peer-review/README.md` says "The final Fable camera and cleanliness rechecks did not complete". This task is the cleanliness recheck completing, and the camera recheck may be retried the same way, so both statements can be stale by publication time. They also name review models and infrastructure failures, which is process noise for an upstream PR. Fix: after the round-three retries land, refresh `review-status.json`/README and the PR10 sentence (or drop it and keep only the technical limitation sentences), and strip model/rate-limit references before any upstream submission.

## Clean at this round

bambu-1, bambu-2, bambu-3, bambu-4, bambu-5, bambu-7, bambu-8, bambu-9, wx-1 (code); bambu-6 (code, body); wx-2 (code). Residual items above are confined to the PR10 comment and the PR10/wx-2 bodies plus README currency.

## Limits

No compiler, build, GUI, printer or network was used. Platform claims were checked against source and the pinned wx tree only; source portability evidence is not Windows/macOS compilation. GitHub reachability of the linked evidence commits was not verified. Taste decisions were not reopened. Nothing outside this directory was written.
