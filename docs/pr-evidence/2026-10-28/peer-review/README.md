# Peer-review follow-up evidence

The draft source heads in [heads.json](heads.json) reproduce the recorded combined app/wx trees. [mergeability.json](mergeability.json) records text merges against each base and freshly fetched upstream master; it is not a build result.

[Portable harnesses](harnesses/README.md) contain source and retained final-SHA sanitizer/caller checks plus explicitly historical arithmetic evidence.

[Native scroller follow-up](progress-native/REPORT.md) passes 348 scoped initial/update checks, preserving 24 known unbreakable-name failures. It uses extracted production statements in a private dialog shell, not a full Studio run. [WebKitGTK CSS measurements](webkit-css/REPORT.md) reject an extra DPI-zoom compensation on the tested runtime.

Windows/macOS source paths were reviewed, but native builds/rendering on those platforms remain unverified. Existing screenshots predate these source follow-ups. No application installation or printer interaction was performed during peer review.
