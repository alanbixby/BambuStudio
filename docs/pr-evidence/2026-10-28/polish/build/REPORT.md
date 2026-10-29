# Frozen native integration build

**PASS — open blocking build/validation issues: 0.** This is the authorized implementation/validation task, not a peer-review round or an approval to merge.

Built application `e9617d1a815183350bd9822fb894996aa086f47a` (tree `094d67e9702508a845195e85fb17084db6da74e4`) with wx `0f2037facedf3d92660e7071b6754fe994aa744d` (tree `db3c30ee5fb3043b7798ae0029ef51312fe9fc65`). Both specified upstream bases are ancestors of these exact commits.

New output: `/home/bxb/.local/state/bambu-scaling/build-02.08.04.57/stage/polished-native-bundle`. Studio was not launched or installed. No fork/tracking repository, branch, index, GitHub content, user display/input, profile or printer was changed by this task.

## Source correspondence

All **11,204 app blobs and 6,697 wx blobs** byte-check against the frozen commits, except six documented owned CMake adaptations. Tracked product C++/headers/resources are exact frozen bytes. The 29-path application baseline upgrade was read and synchronized, including current CMake, preset dispatch and include fixes. All seven logical wx diffs from the warm base were synchronized, including interface docs and Windows/macOS source. The wx sync also canonicalized existing CRLF checkout bytes to their Git-blob representation.

`source-byte-manifest.json` records every path, Git blob, SHA-256, synced file and exception. `baseline-29-review.json` records each baseline change. The six owned adaptations retain header alignment, the existing frontend frozen-lockfile/ignore-scripts policy, job caps and the wx patch hook. They are confined to the owned workspace. No helper hook was copied into a fork.

Warm Git metadata remains app `f977235e6d736c4c0b650520ac5a5b72cbfe9244` / wx `7c74234803455026ec7287827bd545e5a8ed79b7`. This is a warm incremental build with complete frozen source-content correspondence and explicit build adaptations. It is not presented as a pristine checkout build. Bundle compatibility metadata retains those original base IDs; provenance accurately records the reviewed frozen commits/trees and baseline upgrade.

The reachable compile commands and Ninja dependency records checked **716 compiled product source files**, **2039 tracked product dependencies** and **26 generated build headers**. See `compiled-inputs.json`. Generated frontend dist is byte-identical to the previous protected bundle.

Before mutation, source diffs/status, scripts, patches, logs, build records and protected bundle metadata were preserved under `/home/bxb/.local/state/bambu-scaling/build-02.08.04.57/logs/before-polish-loop`. Full restoration patches are `actual-owned-app.patch` and `actual-owned-wx.patch`; forward/reverse byte checks and the idempotent production wx hook passed (`restoration-results.json`).

## Checks run

Commands below ran from `/home/bxb/.local/state/bambu-scaling/build-02.08.04.57` with `env.sh` and owned TMPDIR; compilation was sequential between builds and never exceeded 12 jobs.

- `bash build-native-wx.sh`: passed; actual installed static archive contains the built GTK window/control objects, without replacement objects.
- `bash build-app.sh`: passed, all 370 compile/link steps. Release, GTK3, public=1, Beta=2; actual cache, commands and generated identity header are in `build-records/`.
- `bash probes/run-polished-probes.sh`: passed 36 actual installed-archive range/conversion processes and 3 no-frame processes. Unset/0 preserves identity; 1 enables the frozen conversion algorithm. Font DPI 72/96/120/144/192, GDK scale 1/2, same-process DPI changes, sizes/points/scalars, member/null/window calls, signed coordinates, zero/-1, integer endpoints and saturation thresholds were checked. Six native label cases and the wrapped-label/button exclusions passed.
- `python3 /tmp/bambu-polish-20261028/implementation/build/build-system-options-off.py`: complete 613-step native wx build and separate owned-prefix install passed with `wxUSE_SYSTEM_OPTIONS=0`.
- `bash probes/run-polished-options-off-probe.sh`: ten separately installed zero-options archive processes passed at 96/120/144/192 and dynamic DPI, GDK scale 1/2. The real disabled header omits SetOption; the harness guards that call and uses the real GetOptionInt zero stub plus archived conversions. One initial harness compile error is retained in `logs/polished-options-off-probe-initial-error.log`; no app/wx source fix was needed. Enabled preprocessed harness tokens before/after the guard are byte-identical (`logs/polished-enabled-harness-preprocessing.log`).
- Main app and wx freshness commands both reported `ninja: no work to do.` The separate build left all 16 production wx archive hashes unchanged.
- `python3 assemble-bundle.py --native --destination stage/polished-native-bundle`: passed; **6887 files hashed**.
- `python3 /tmp/bambu-polish-20261028/implementation/build/verify-polished.py`: passed full read-only tracking `source_bundle._load`, source-byte checks, archive/object provenance, frontend preservation, startup disassembly, all 28 ELF/DSO ldd checks, protected bundle/install checks and clean fork status.

The linked Linux ELF calls SetOption with 1 before `on_init_inner()`; see `app-oninit-disassembly.txt`. This is compiled-code evidence, not a Studio startup trace. All archive probes use the actually installed archives. The zero-options library uses a separate prefix; it is not packaged into the app.

## Artifact and protection checks

- ELF SHA-256: `e25ee5adf9b6af148bdf9e79265cc3ad0f1c59a73e59cfc38a84f3e764a93c3d`
- Bundle fingerprint: `997f53d088afec2f57bc8e69d3fb81e71edd41e67a4fd36e277f375d7857aad4`
- RUNPATH: exactly `$ORIGIN`; no workspace path. All 28 ELF checks resolve with no missing dependency or sysroot/dependency-prefix resolution.
- Native mode has no fixes directory, preload libraries or legacy fractional-DIP launcher flag.
- `clean-native-bundle`, `source-bundle`, `dip-screening-bundle`, `peer-reviewed-native-bundle` (2170f1da…) and installed 5029c1 retain their complete fingerprints, metadata, inventory and ELF bytes. Exact before/after evidence is in `protected-before.json` and `verification.json`.

## Limits

Linux x86_64 Release integration only. Windows/macOS source was synchronized but neither OS was compiled or run. No GTK2, Debug or C++98 native library build was performed. Focused native probes use private Xvfb, hidden/no-frame wx harnesses and no event loop; they do not establish complete Studio runtime behavior. The completed camera suite was not rerun. No screenshots or PR changes were made. These results make no all-OS or merge-readiness claim.

Full logs are in `logs/`, probe sources/commands in `probes/`, actual build flags/metadata in `build-records/`, structured results in `probe-results.json`, `compiled-inputs.json`, `verification.json` and `findings.json`. Inherited upstream whitespace/compiler warnings remain in the logs; frozen source was preserved.
