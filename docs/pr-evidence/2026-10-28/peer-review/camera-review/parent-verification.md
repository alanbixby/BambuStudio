Recovered camera R3 evidence verification completed at 2026-10-28 08:32:58 UTC.

The requested source identity and model results are verified. This is evidence verification, not another peer-review round. Fable's report records zero open blockers and two nonblocking observations, CF-10 and CF-11; those are the review's classifications, not a new correctness verdict from this verification.

- PR10 head: df28193c8e4aa5f2439f81eed83caa842a01c5ea; base: 79df7ae309be398ed30c9f397c13c9911c2edc57.
- Reviewed combined: e79eb4721427ac7f136d6d5c5fa0acd962f57f30.
- Final combined and clean upstream checkout HEAD: 47a28ade55ec26d12096151f8ad7d93ebde174bc.
- DeviceWebHost.cpp blob is 0db7cf8f5d4079ec0bde3d7cba4fc708bb0ca6dc in PR10, reviewed combined, and final combined.
- All six PR10 paths are byte-identical between reviewed and final combined and match the current upstream checkout files. Five are also identical to the standalone PR10 files. StatusPanel.cpp as a whole differs from standalone PR10 in unrelated hunks; its fit_camera_to_feed method is identical.
- Extracted fit_camera_to_feed method: 5,402 bytes, SHA-256 41a71da22f4ed091f5556a3f747b4638b4555c43f3d975a7918b7eb62f610b8d in round-two head 6e81cd8f92313dfa8c693baab022a18945f74add, PR10 head, reviewed combined, and final combined.
- Reviewed-to-final combined diff touches only Widgets/ComboBox.cpp, Widgets/ComboBox.hpp, and Widgets/TextInput.hpp: 10 insertions, 19 deletions. No camera code changed.
- Round-two-to-PR10 delta is DeviceWebHost.cpp only, 5 insertions and 3 deletions. git diff --full-index matches round3/camera-delta.patch exactly (SHA-256 87afc9ffa5c3ba2c12159fc6cd8815f2dbb9743fda12105c375935a1debb0a5f).
- Existing source-patches/review/bambu-10-camera-ams-balance.patch matches git diff --full-index base..head byte for byte: 16,064 bytes, SHA-256 f97440c5e41c652da263553ae392f64ff7586587ac30d0ab59a89ecae2c90129.

Ran the unmodified raw pending_zoom_model_r3.py with python3 -I. Exit status 0; stderr empty. A supplemental isolated verifier reran its cases and asserted the aggregate counts, also exit status 0 and empty stderr.

- 168 cases: 3 scales x 4 window classes x 7 page heights x 2 backend-readiness variants.
- Exactly one distinct zoom across pre-report passes in every case; no modeled pre-report drift.
- All 84 delayed-backend cases make zero modeled zoom API calls before readiness.
- Six final-versus-reference differences, all CF-10 examples: wide window, page height 344, at scales 1.0/1.5/2.0 and both readiness variants. Final zoom 1.60 versus report-first reference 1.55. The other 162 cases match their reference.
- Across the 168 standard cases, maximum distinct post-report zoom values is 1; the model prints zero cases with more than one post-report zoom change.
- Synthetic Edge wide-first detail reproduces SetZoomFactor values [1.6, 2.0, 1.6], final/reference both 1.6.
- Old-head contrast reproduces pre-report [1.6, 2.0, 2.0], followed by post-report [1.6, 1.6].
- All 105 base-height rounding checks pass: 5 scales x 21 zoom steps. Zero failures.

Byte comparisons against the linux-fixes evidence/peer-review-20261028/round3/camera_fable directory at the snapshot time found no changed report, findings, or model bytes:

- REPORT.md: 3,815 bytes, SHA-256 c012df81cad2fde50c6f7f6456455941ac2257c61ea200738b175cf0c495dad9; raw, tracking worktree, and committed HEAD copies match.
- findings.json: 7,420 bytes, SHA-256 d74bf5b33c1fd972c7c4fdc1fc84f28de9ec9848d346d5e1f80e643e85f242ac; raw, tracking worktree, and committed HEAD copies match.
- pending_zoom_model_r3.py: 8,202 bytes, SHA-256 55152203e931a5546a0e687252faa1ff27c59441fcbb522b851db755bbbc7e38; raw and tracking worktree match. It was newly copied and untracked at this snapshot, absent from committed HEAD. The parent was independently updating STATUS.md and adding recovered-status.json; this verifier did not modify those files.

Evidence wording caveat: the report's "backend ready ... after three fit passes" is not literally exercised by this Python model. state['n'] stays zero during the entire pre-report loop and is assigned ready_after after that loop. The delayed cases actually perform one or two pre-report passes. The supported statement is "backend unready throughout pre-report fitting, then ready for the first content report." This does not alter the zero-unready-call or no-drift counts.

Diagnostic caveat: the model's base_h_pre field is a bound method, and min_pre is collected after post-report fitting. Their labels do not supply valid pre-report measurements; stdout therefore contains nondeterministic Python object addresses. The supplemental cases.json omits the bound method and retains the remaining original fields. No model code was edited.

Source/model correspondence was checked against the host clamp, synthetic 340 height, zoom readiness gate before jitter returns, synchronous panel min-size handler, GetBaseHeight division, and fit solver expressions. The model retains assumed panel geometry and a hypothetical width-dependent first report; it is not a compiled extraction of the full wx event loop. No GUI, compilation, installation, printer, network, GitHub, source edits, commits, or delegation were performed. All verifier writes are confined to /tmp/bambu-camera-r3-recovery-verification. No broad correctness, mergeability, or cross-OS runtime claim is made.

Machine-readable identities, hashes, assertions, and stable case details are in verification.json and cases.json. model.stdout.log is the direct model run; model.stderr.log is empty. verify.py and verification.stdout.log document the supplemental verification; verification.stderr.log is empty.
