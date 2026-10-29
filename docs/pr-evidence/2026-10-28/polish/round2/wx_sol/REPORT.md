# Sol review, round 2 — wx and Bambu integration

**Open blockers: 0. Open non-blocking findings: 0. New findings: 0.** Both prior findings are resolved by the actual candidates. This partition has converged; no round 3 is requested. This is a source/evidence review of personal-fork draft candidates, not approval to submit upstream or a claim of all-platform readiness.

## Exact review scope

Source and descriptions reviewed:

| Candidate | Exact head | Exact base | Added/deleted |
|---|---|---|---|
| wx-01 | `14a14a773c74ae23281417f58334b5c28ecfed12` | `abb542694ef4534a50e65c5b877b2774d02952ae` | 24/0 |
| wx-02 | `d54f3313028fc439cea91f0b6a213e5ad2245b90` | `abb542694ef4534a50e65c5b877b2774d02952ae` | 91/3 |
| bambu-05 | `305b41867feec57eb3d535d59920a9f091991762` | `79df7ae309be398ed30c9f397c13c9911c2edc57` | 66/63 |
| bambu-progress | `5608a478ca983cc63083627bb6f8854f575412db` | `305b41867feec57eb3d535d59920a9f091991762` | 9/10 |
| bambu-gtk-integration | `e77253cd2ff240df00890d2e798faa312df23e95` | `5608a478ca983cc63083627bb6f8854f575412db` | 7/2 |

Integration heads: app `e9617d1a815183350bd9822fb894996aa086f47a`, wx `0f2037facedf3d92660e7071b6754fe994aa744d`. Also inspected exact release heads `b506005bc4ee62124e24bf00e0f58656db3646a6` and `f5e51a20bd328d4a043af9344825d7347270c2c9`. Current upstream wx base is the supplied `abb542694ef4534a50e65c5b877b2774d02952ae`; this review makes no assertion about later upstream changes.

All sixteen candidates received independent SHA/base/parent/commit-count/path/numstat/body-image metadata checks. Their exact heads and body hashes are in `verification.json`. Source/body conclusions here concern the five candidates above and their integration context; the other eleven belong to other review partitions.

## Prior findings and parent responses

**WXSOL-001 — resolved; originally blocking.** I accept the default-off design and withdraw the previous release-backport/pin requirement for this implementation.

At wx-02 head `d54f3313028fc439cea91f0b6a213e5ad2245b90`, `src/gtk/window.cpp:4394` reads the option and returns scale 1 before `window->GetHandle()` or any GTK access. `FromDIP`/`ToDIP` return the original size when scale is 1 (`:4438`, `:4448`). At the pinned head, `include/wx/sysopt.h:59` supplies the existing zero accessor when `wxUSE_SYSTEM_OPTIONS=0`; it does not require a new stub or framework. The option is documented as default 0, set before windows and then left unchanged (`interface/wx/sysopt.h:91`). Explicit environment activation remains possible through the existing system-option mechanism; that is opt-in, not a default release-wide change.

Both sampled release recipes still say `GIT_TAG master`, and neither exact release tree contains the new option name. Their existing measured-size errors are therefore not newly activated merely by obtaining wx-02. They do not need source backports to preserve the previous default conversions. This conclusion is scoped to the sampled releases and explicit default-off behavior, not an exhaustive support-branch inventory.

Bambu integration head `e77253cd2ff240df00890d2e798faa312df23e95`, `src/slic3r/GUI/GUI_App.cpp:2909`, guards the setter with `__WXGTK3__ && wxUSE_SYSTEM_OPTIONS`, and enables it before `on_init_inner()` and subsequent font/splash/window creation. The constructor and startup source were read. The same two integration blobs occur in the combined app. The live Linux ELF disassembly independently matches the saved evidence: the SetOption call receives 1 before `on_init_inner()`. That is compiled-call-order evidence, not a GUI startup run.

`deps/wxWidgets/wxWidgets.cmake:27` selects `https://github.com/alanbixby/wxWidgets` and exact SHA `0f2037facedf3d92660e7071b6754fe994aa744d`. A fresh read-only `git ls-remote` returned that exact SHA for `refs/heads/review/font-dpi-integration`. A complete Git-tree comparison established that the pin is precisely upstream `abb5426…` plus both candidate changes, with no extra source files or changes. Both candidate heads and upstream are ancestors. Its tree also equals the prior `c7cdfa5b` integration tree. The pin includes the upstream Windows WebView change; that change is not introduced by these wx candidates.

The separate nine-line adoption candidate is concrete and reviewable. Its body discloses the temporary fork pin and requirement to replace it with the accepted revision before upstream submission. That remains a submission condition, not a blocker to these personal-fork drafts. App #5 remains independently useful.

**WXSOL-002 — resolved; originally non-blocking.** The wx-01 body now says, “The check runs while GTK measures a label without wrapping; other widget types keep their existing path.” This accurately describes `src/gtk/control.cpp:356` at `14a14a773c74ae23281417f58334b5c28ecfed12`. `src/gtk/stattext.cpp:237` still temporarily disables wrapping during best-size calculation and restores it at `:251`; the body no longer promises exclusion of every wrapped wxStaticText path. No source fix is needed for this wording finding.

## Independent checks and results

`python3 verify.py` passed **145 recorded Git/binutils commands**, plus read-only hash checks. Full commands/results are in `commands.json`; exact inspected blobs and candidate patches are under this output directory.

- All sixteen exact candidates have one commit with the stated immediate parent, paths and additions/deletions; largest change is 415 lines. The five reviewed patches pass `git diff --check`. This verifies size and structure, not universal mergeability.
- Read the wx font invalidation ownership/freeing, label/wrapping guards, disabled-options accessor, conversion wrappers, saturation/sentinel handling, platform dispatch, and Bambu startup/dependency/unit-correction/progress code. No concrete new regression was found. Windows/macOS conversion branches remain as before; Bambu #5 deliberately changes shared call sites to correct units.
- Independently checked hashes and PASS/no-FAIL contents of **51 supplied native process logs**: 36 conversion, 3 no-frame, 2 label, 10 options-disabled. Read the probe sources and representative raw dynamic-DPI/label logs, including zero stable invalidations. The wrapped-label exclusion probe tests the directly wrapped GTK measurement case, not a promise that all wxStaticText wrapping paths bypass the check.
- Rehashed both live static archives and the live application ELF. Extracted and hashed the production archive's window/control members using `ar p`; hashes match the recorded members and frozen-source hashes. Compared **21 compiled C++ path records** (20 unique source paths) and their live source bytes with the exact combined app blobs. Independently regenerated startup disassembly using `objdump`; it matches the supplied evidence byte-for-byte. No executable was run.
- Read the full native build report, the separate 613-step options-disabled build's raw completion log, compiled-input/byte manifests, and documented six CMake adaptations. The warm-build qualification is justified and retained. Checked that immutable evidence README at app commit `9ea10ea751a655b1c964f08ac4b2ce95bef07622` matches the staged copy.
- The five descriptions state the behavior, material limits and screenshot provenance without excessive prose. Images are retained and explicitly attributed to earlier combined Linux builds. No wording promises final isolated-PR visual acceptance.

## Limits

No builds, new native probes, program execution, GUI input, installation, profile/printer access, repository/index/branch edits, pushes, PRs, GitHub comments or further delegation occurred. All writes are within this assigned scratch directory. The portable Python script performs source/metadata/hash correspondence checks only; existing native results were inspected, not reproduced.

Windows/macOS have not been compiled or run; no new GTK2/GTK4, shared-library, native Wayland, Debug or C++98 native-library validation was performed. Supplied native probes use private Xvfb and hidden/no-frame harnesses without the Studio event loop. The paired build is warm with six disclosed local CMake adaptations. None of these limits alone proves a regression, and this report makes no all-OS, complete end-user behavior, or final merge-readiness claim.
