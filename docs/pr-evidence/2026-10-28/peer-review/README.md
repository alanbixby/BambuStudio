# Peer-review follow-up evidence

The draft source heads in [heads.json](heads.json) reproduce the recorded combined app/wx trees. [mergeability.json](mergeability.json) records text merges against each base and freshly fetched upstream master; it is not a build result.

[Portable harnesses](harnesses/README.md) contain source and retained final-SHA sanitizer/caller checks plus explicitly historical arithmetic evidence.

[Native scroller follow-up](progress-native/REPORT.md) passes 348 scoped initial/update checks, preserving 24 known unbreakable-name failures. It uses extracted production statements in a private dialog shell, not a full Studio run. [WebKitGTK CSS measurements](webkit-css/REPORT.md) reject an extra DPI-zoom compensation on the tested runtime.

Windows/macOS source paths were reviewed, but native builds/rendering on those platforms remain unverified. Existing screenshots predate these source follow-ups. No application installation or printer interaction was performed during peer review.

## Review availability

All twenty-six delegated reviews completed. Both final Fable rechecks resumed automatically after their initial API rate limits and completed with zero blockers. [Completed cleanliness review](cleanliness-review/REPORT.md) and [parent responses](cleanliness-review/RESPONSES.md) record the final comment/description follow-ups. The final Print Options reduction passed its Codex review. The startup sizing fix has both a [completed independent camera review](camera-review/REPORT.md) and a parent-authored extracted-method regression check in [startup-zoom-model](startup-zoom-model/README.md). The installed application was not changed.

## Linux integration build

The exact alpha/pinned-wx integration bundle for the final source passed build, freshness, 6,887 file hashes and 28 dependency checks. [Build record](linux-build.json) and [independent bundle check](bundle-parent-check.json) record fingerprint `2170f1da3c1c` and its exact ELF identity. The bundle was neither installed nor launched; this is not Studio runtime acceptance or a Windows/macOS build.

The [original partial-review record](partial-camera-review/STATUS.md) is superseded by the completed camera review. Its 168 host/solver model cases confirm the startup correction. Existing small-height jitter filtering and possible first-layout WebView2 reflow remain accepted nonblocking limits; neither native Windows nor macOS rendering was tested.

The final combined source `1f880d3` and PR10 `fab83eef` add only a constant-reference comment after reviewed/built `47a28ade` / `df28193c`. [Exact delta](cleanliness-review/comment-only.json) and [independent composition check](cleanliness-review/parent-verification.json) preserve that distinction. No rebuild was needed for the comment; the bundle record remains unchanged.
