# Pending AMS zoom contract test

These frozen C++ units contain actual extracted host/panel methods and the content-size callback. wx windows and browser operations are doubles; this is not native Windows/macOS compilation or paint-timing evidence. The non-macOS baseline reproduces a base-height mismatch before the first page size. The correction passes 840 non-macOS and 40 macOS-branch state checks.

Baseline methods match PR10 ancestor `6e81cd8f92313dfa8c693baab022a18945f74add`; corrected methods match `df28193c8e4aa5f2439f81eed83caa842a01c5ea`. The result JSON records local combined refs used for extraction; source-method equality was checked against the focused commits. Compile with C++17, warnings as errors and UBSan. Run the baseline non-macOS executable expecting exit 1 and the exact pending-height message; corrected non-macOS and both macOS-branch executables must exit 0. Define `__WXOSX__` only to select the extracted branch in this model, not to simulate native Cocoa.

Fable's final recheck could not run because its API rate limit was reached. This parent-authored test does not replace that missing independent review.
