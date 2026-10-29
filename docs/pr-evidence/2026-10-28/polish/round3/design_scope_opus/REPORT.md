# Design/scope review, round 3 (final): design_scope_opus

**Open blocking: 0.** Open non-blocking: 1 (DS-R3-01, wording only).

## Final heads reviewed
14 app heads are unchanged from round 2. Two are new:
- bambu-ams-zoom `a273fd21b1580662221037549e09bd7e10bcc615` (parent bambu-10 `bed9f5a1`)
- bambu-gtk-integration `74a75752f34633a5bb00d8a96bc6a30fc9a2744a` (parent bambu-progress `5608a478`)

The full list is in findings.json. App combined head: `e9617d1a`. wx integration: `0f2037fa` (base `abb54269`).

## Round-2 findings
| ID | Status |
|---|---|
| DS-R2-01 screenshot attribution | Resolved. The captions now say there is no isolated screenshot yet, and the Project captions say the images don't distinguish the two causes. One wording slip carried to DS-R3-01. |
| DS-R2-02 per-call option lookup | **Conceded.** Caching on first use would quietly lock the feature off if something called FromDIP(NULL) before OnInit. The documented contract is only "before creating windows". wxGTKDIPScale already reads the screen DPI on every call by design. The cost is still unmeasured; it belongs in the review evidence, not the body. |
| DS-R2-03 progress stacking | Resolved. The body now says the progress PR also applies to master on its own. |
| DS-R2-04 comment noise | Resolved. The 2-line comment moved from AMS zoom to the GTK adoption PR, nothing else changed, and both PRs are still one commit. |
| DS-R2-05 jargon | Resolved. |
| DS-R2-06 OS clarity | Resolved. The body now says "GTK3-only on top of current upstream master". |

All round-1 findings stay resolved or conceded as recorded in round 2.

## New finding
**DS-R3-01 (non-blocking).** In bambu-05, wx-02 and bambu-gtk-integration, the new alt text calls `stock-sidebar-cards-before.png` "Combined-series sidebar before the card-spacing fix". That image is the original app (stock filename; its earlier caption was "Original printer/plate row"). So the pair compares the original app with the whole series, not the series with and without #8. "The card-spacing fix" also doesn't name its PR, which matters in the wx repo.

Fix: use the alt text "Original sidebar" / "Sidebar with this whole series applied", and name BambuStudio #8 in the caption.

## Checks run
- `git diff 54083d6f a273fd21` and `git diff e77253cd 74a75752`: the same two comment lines swapped between the two PRs. `bed9f5a1..a273fd21` no longer touches the comment.
- `recompose.sh` (in this directory; text-level only, no build): applied the 14 app diffs in stack order to `79df7ae3` copies. Byte-identical to `e9617d1a`: ok=43, bad=0.
- Diffed bodies-round2 against bodies-round3 and read every changed line.
- The app repo working tree was unchanged.

## Limitations
- Source and text review only: no build, launch, screenshots, or Windows/macOS compile or run.
- Isolated per-PR screenshots are still missing for 5 PRs (disclosed in their bodies).
- Project threading and WebView runtime are out of this partition.
- No all-OS or merge-readiness claim.
- This was the last allowed round. I did not start another.
