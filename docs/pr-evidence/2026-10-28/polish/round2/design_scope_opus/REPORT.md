# Round 2: design, scope and taste review (Claude Opus 5.5)

**Open blocking findings: 0.** Six non-blocking findings (DS-R2-01..06). Of the 12 round-1 findings, 8 are resolved and 4 are conceded. Machine-readable version: `findings.json`.

## Reviewed heads
Full SHAs are listed in `findings.json` → `reviewed_heads`. App base: `79df7ae309be`. wx base: `abb542694ef4`. Combined app: `e9617d1a8151`. wx integration: `0f2037facedf`.
Stacks: `bambu-05 → bambu-progress → bambu-gtk-integration` and `bambu-10 → bambu-ams-zoom`. Every other candidate sits directly on master.

## Commands and results
- For each candidate, `git rev-list --count base..head` returned 1 (16 of 16). `git diff --shortstat` matches `curated-prs.json`. The largest is bambu-03 at 415 changed lines.
- **Recomposition (independent of the parent's check):** I applied the 14 app candidate diffs in stack order to copies of the 43 changed files taken from 79df7ae3. The result is byte-identical to `e9617d1a` (ok=43, bad=0).
- **bambu-progress on master:** `git apply --check` of `305b4186..5608a478` against 79df7ae3 copies succeeds (rc=0).
- **wx pin scope:** `git diff --stat abb54269 0f2037fa` changes only GTK-guarded code, docs, and one header guard that is identical for non-GTK3 ports.
- **Screenshots:** I viewed the shared sidebar before/after pair directly.
- Scratch files are in `scratch/` (`recompose/`, `prog/`). I did no builds, GUI runs, repo writes or GitHub writes.

## Prior findings
- **Resolved:**
  - R1-01: Project work split into native and JS PRs.
  - R1-02: camera fit and AMS zoom split.
  - R1-04: 129-line mechanical DPI PR and 19-line progress PR.
  - R1-06: Assembly sidebar PR now on master.
  - R1-07: title and body now cover all settings tabs.
  - R1-08: the helper no longer wraps or lays out; callers lay out once.
  - R1-09: one commit per PR with plain subjects.
  - R1-10: both wx candidates rebased onto abb54269.
- **Conceded:**
  - R1-03: the AMS zoom cap is now named once and stays at 2.0. The user explicitly accepted it, and the split lets upstream take the camera fit on its own.
  - R1-05: the always-shown scrollbar is disclosed in the body.
  - R1-11: the comment cross-reference is enough.
  - R1-12: using `Http::url_encode` avoids app access from the worker thread.

## New findings (all non-blocking)
- **DS-R2-01, screenshots:** bambu-05, the GTK integration PR and wx-02 reuse bambu-08's sidebar before/after pair. The visible difference in that pair is #8's card change, not theirs. bambu-03 and project-startup share one pair without saying which fix the before-state needs.
  - Fix: capture PR-specific images (for wx-02 and the integration PR, opt-in off vs on at Xft.dpi 144), or say plainly that no isolated image exists yet.
- **DS-R2-02, wx-02 cost:** each FromDIP/ToDIP call now runs `wxSystemOptions::GetOptionInt`. When the option is unset, that includes string building plus up to two `getenv` calls, where it used to be an inline no-op.
  - Fix: read the option once. Caveat: a FromDIP call made before the app opts in would lock it off. Bambu opts in on the first line of OnInit, so it is safe.
  - The API itself is a single system-options flag, which is standard wx practice and not over-designed.
- **DS-R2-03, stack:** bambu-progress does not depend on bambu-05.
  - Fix: keep the stack and add one sentence to the progress body saying it is stacked only for merge order.
- **DS-R2-04, diff noise:** the AMS zoom PR rewrites a comment in `OnWebContentSizeChanged` that has nothing to do with zoom.
  - Fix: drop that change.
- **DS-R2-05, wording:** a few process or jargon phrases remain, such as "accepted 2× limit", "reviewed revision", "identity conversion", "coordinate sentinels" and "fixtures". Plain alternatives are in `findings.json`. Fable owns the final wording.
- **DS-R2-06, OS clarity:** the wx pin changes no Windows/macOS wx code compared with today's bambulab master. The integration body should say so instead of only "untested".

## Safety check of the Codex-authored opt-in (source reading only)
- **Default off:** the scale is 1 before any GTK call, so apps that don't opt in keep their current conversion.
- **Other ports:** the header still uses the inline identity for MSW, OSX and Qt. GTK2 is untouched.
- **No window:** a NULL window falls back to the default screen, and to 1 if there is no screen.
- **Opt-in placement:** the app sets the option behind `__WXGTK3__ && wxUSE_SYSTEM_OPTIONS` at the top of `OnInit`.
- **Older wx:** with an older wx the option does nothing, so the previous conversion stays.

I found no needless API surface.

## Limitations
- I did not compile, run, or measure anything on any OS. DS-R2-02 is based on reading the code only.
- I did not review the following; they belong to other partitions:
  - Project threading and the removal of old auxiliary-root deletion in bambu-03 (project_astra).
  - WebKitGTK/WebView2 zoom at runtime and wx GTK runtime behaviour (native_sol, wx_sol).
- I make no claim that the PRs work on all OSes or are ready to merge.
