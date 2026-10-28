# PR6 round-three review

Open blocking count: **0**. One non-blocking candidate-description mismatch. No new code defect established.

## Frozen inputs

- PR6 head: `cbde5d139ced56b5e3d7def490446f06ccd2e791`
- PR6 base: `79df7ae309be398ed30c9f397c13c9911c2edc57`
- Final application combined commit: `47a28ade55ec26d12096151f8ad7d93ebde174bc`
- wx base: `e2fa9bda52f720242e35def30ac4a01fbe75f5a8`
- wx combined: `3fea0af433d9630f79eaf8fbfc062364ba456be3`

Read the final-heads map, isolated diff, font-plumbing removal delta, current candidate body and immutable source. No refs, repository files, caches, installed files, GUI, processes, profile or printer were changed. No delegation or GitHub operations.

## Prior objections and final simplification

**CF-01: resolved.** All four Widgets/TextInput.cpp/.hpp and Widgets/ComboBox.cpp/.hpp blobs equal the PR base at both final PR6 and the final application combined commit. Ordinary TextInput appearance and editable ComboBox behavior remain baseline. There is no new generic API, null initialization or protected measurement exposure.

**R1-PRINT-FONT-001: closed by removing the introduced exposure.** This is not a claim that baseline arbitrary editable font resizing is repaired. The new propagation and native-height fallback are absent. The final patch only calls the existing font method on readonly selectors.

The five controls are `ai_monitoring_level_list`, `spaghetti_detection_level_list`, `purgechutepileup_detection_level_list`, `nozzleclumping_detection_level_list` and `airprinting_detection_level_list`. At `cbde5d139ced56b5e3d7def490446f06ccd2e791:src/slic3r/GUI/PrintOptionsDialog.cpp:1011-1018`, `1049-1056`, `1092-1098`, `1132-1138` and `1171-1177`, respectively, each construction explicitly uses `wxCB_READONLY`; its Body_12 call precedes item population and initial selection. No local direct native-child access changes that state.

The unchanged ComboBox constructor hides the child at Widgets/ComboBox.cpp:51-53. The existing SetFont branch at :199-204 therefore updates the outer control. SetSelection (:83-88) routes the selected text through SetLabel (:149-165), which measures the outer label through TextInput::SetLabel (:117-121). TextInput::render (:330-332) explicitly paints using `GetFont()`. This retains the requested smaller selected-value font without touching native editable-entry font or Cocoa sizing APIs. The native child stays at its baseline font/height, but it is hidden in these five controls. No claim is made that the popup items themselves acquire Body_12.

Removing the null initializer does not create a new constructor path: the TextInput base constructor's SetFont call (:34) cannot dispatch to a derived ComboBox override, and TextInput::Create clears `text_ctrl` (:63) before native window creation (:64). All these statements describe unchanged baseline code. TextInput::messureSize (:395-423) retains allocated height and only increases it to accommodate the child; speculative child resizing would not establish a smaller outer height.

The Print Options auto-wrap labels and guarded layout/FitInside passes remain. This last simplification does not alter those round-two dialog blobs except for removing the independent widget plumbing; no new platform API or include dependency is introduced by the final delta.

## R3-PRINT-FONT-001 — non-blocking description mismatch

Affected PR: alanbixby/BambuStudio#6. Candidate `/tmp/bambu-peer-review-20261028/round2/bodies/bambu-pr-6.md:3` still says the hidden native entry receives the font and native line height. Line 5 still describes validation of a narrowed override and constructor guard. Those changes are absent at the final head. The exact read is preserved in `candidate-body-read.md`; SHA-256 `ca9e99173cf3e1a51e7c3237e7c9508a874708fceb7135349988528d2f47131f`.

Trigger: publishing that candidate body with this head. Reviewers on any OS would be told the patch changes a generic native sizing path that it deliberately removes. Replace the stale paragraph and validation sentence with the actual five local readonly font calls, unchanged widget behavior, final source checks and appropriately labeled historical evidence. Verify against the final two-file diff and ComboBox.cpp:199-204. No code change or further review round is needed for this wording correction.

## Fresh validation and limits

`python3 source_checks.py` passes **29/29 static checks**: governing SHA map, two-file diff scope, eight baseline widget-blob comparisons, two isolated/combined dialog comparisons, five readonly constructions, font-before-content ordering, absence of direct native-child mutation, exact five added font calls and `git diff --check`. Evidence is in `source-checks.json`. An initial ordering-check implementation searched for earlier selection calls outside construction; that check was corrected to search after each constructor before the final passing run. This was a review-script issue, not a source failure.

No compiler, build, GUI/native runtime probe, printer command or remote check was run. Native Windows/macOS compilation/rendering, translations, popup/focus behavior, scrollbar settling and DPI transitions remain validation limits. Historical combined screenshots and prior tests were not counted as fresh final-head validation. Source tracing and blob identity are not native cross-OS compilation.
