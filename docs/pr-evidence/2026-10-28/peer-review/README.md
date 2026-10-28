# Peer-review follow-up evidence

The draft source heads in [heads.json](heads.json) reproduce the recorded combined app/wx trees. [mergeability.json](mergeability.json) records text merges against each base and freshly fetched upstream master; it is not a build result.

[Portable harnesses](harnesses/README.md) contain source and retained final-SHA sanitizer/caller checks plus explicitly historical arithmetic evidence.

[Native scroller follow-up](progress-native/REPORT.md) passes 348 scoped initial/update checks, preserving 24 known unbreakable-name failures. It uses extracted production statements in a private dialog shell, not a full Studio run. [WebKitGTK CSS measurements](webkit-css/REPORT.md) reject an extra DPI-zoom compensation on the tested runtime.

Windows/macOS source paths were reviewed, but native builds/rendering on those platforms remain unverified. Existing screenshots predate these source follow-ups. No application installation or printer interaction was performed during peer review.

## Review availability

Twenty-five delegated reviews completed. The final Fable camera recheck resumed automatically after its initial API rate limit and completed with zero blockers. The final Fable cleanliness recheck remains unavailable. The final Print Options reduction passed its Codex review. The startup sizing fix has both a [completed independent camera review](camera-review/REPORT.md) and a parent-authored extracted-method regression check in [startup-zoom-model](startup-zoom-model/README.md). The installed application was not changed.

## Linux integration build

The exact alpha/pinned-wx integration bundle for the final source passed build, freshness, 6,887 file hashes and 28 dependency checks. [Build record](linux-build.json) and [independent bundle check](bundle-parent-check.json) record fingerprint `2170f1da3c1c` and its exact ELF identity. The bundle was neither installed nor launched; this is not Studio runtime acceptance or a Windows/macOS build.

The [original partial-review record](partial-camera-review/STATUS.md) is superseded by the completed camera review. Its 168 host/solver model cases confirm the startup correction. Existing small-height jitter filtering and possible first-layout WebView2 reflow remain accepted nonblocking limits; neither native Windows nor macOS rendering was tested.
