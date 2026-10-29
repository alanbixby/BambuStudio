# Camera-only split — focused implementation verification

**PASS within the disconnected native GTK fixture. Open findings: 0.** The camera-only intermediate was compiled and executed directly; this result is independent of its combined camera/AMS sibling. No source changes are requested by this verification.

## Exact tested inputs

- Candidate `polish/camera-ams-balance`: `bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7`.
- Entire unmodified extracted helper starts at production `StatusPanel.cpp:2043`; 35 extracted lines. It contains no AMS reference or conditional build macro.
- The fixture has no BBL AMS macro and renames its synthetic AMS member, while including the actual function unchanged. Its zoom setter records calls. The native sizer/layout structure and event-pumping sequence come from the original compact probe. `fixture.diff` documents every fixture adaptation.

SHA-256 hashes:

- StatusPanel.cpp: `c469e4c1123197f01a0ae2bb3a6baee9adb54a2a9f41bad5415f0185ea4c2e26`.
- StatusPanel.hpp: `1e43e84f594e21eeabc0921d1f6a018e98976f0f065059354ac9c5a8325ed3ad`.
- Extracted function: `921d802182694875625db7f9309a7417f73017a8c118c38a96b5e9ac0575aabd`.
- Original compact fixture: `b5f0ad0321580b68d14c5fdb889510c1b51dbe18bc54d36e49d7e03260fc995d`.
- Tested fixture: `3d702368cd07076ee0a27a6c59ff9f755113b75deeddcbb319961b643677d4e6`.
- Private wx header manifest (canonical sorted JSON): `fb4fe0d2a4d239a3abeac9093eb0c3d5be735c65993b39c38a5472a4545b1eca`. Individual header hashes are in `inputs.json`.

- Sealed `libwx_gtk3u_core-3.1.a`: `53da679b427c37a72300985c81c7f779182d32066fe9881a4812ee76dccedc7a`.
- Sealed `libwx_baseu-3.1.a`: `d281166b58c5f8e7128292e731f5b5983641599ea3ebf7b670f3e0c3859a81c1`.
- Sealed `libwxregexu-3.1.a`: `d923f84fd215adbb7efa2670252752f8f9e6b14c500d2d1ed3866d01195981f2`.
- Sealed `libjpeg.a`: `44bb57bb298b0620729d1730beef033a4610ad5f6b9b3b840e7c0bc09aae0cb9`.
- Sealed `libpng16.a`: `9d1cbac7294331348a09f575178bbce3999ffbd66a05a985d60978247931bb86`.
- Sealed `libtiff.a`: `eea25d1fb5315347decf5067150e63e4c647525f95ab3ef122e5a127f3a76439`.

All private archive and header hashes match the sealed original provenance. Stated wx commit: `3fea0af433d9630f79eaf8fbfc062364ba456be3`; archive bytes do not independently establish Git identity. No warm wx archive/header/config was accessed. The exact compiler command and dependencies are retained.

## Matrix and observations

One compiler invocation succeeded. All 8 probe processes exited0, producing 80 phase observations: six hidden-AMS cases at96/144/192 font DPI × GDK scale1/2, plus shown-unzoomed AMS at96/scale1 and192/scale2. Native `FromDIP(96)` was96/144/192 respectively; native GDK scale matched each request.

Each process runs wide2200 → narrow1400 → undersized1000 → boundary1218 → narrow1400 → wide2200 DIP, then grows height520 →1100 →520, narrows again, and executes one extra queued helper call. The final trigger is synthetic; no real media event is claimed.

- All80 observations have zero unnecessary horizontal extent. Fitting clients have matching virtual widths; undersized clients retain the natural minimum and required scrolling.
- At96 DPI/scale1 with AMS hidden: wide client/virtual width2185, narrow1385/1385, undersized985/1218, then wide2185/2185. Control minimum shrinks1581 →781, releases to default -1 at undersize, and returns1581 at wide.
- Control natural width stays614 DIP:614/921/1228 native units at96/144/192 DPI. Measurement uses the actual Control sizer CalcMin result, separately checked against the original fixture natural minimum. No unexpected minimum change occurred.
- Camera width never falls below its natural minimum. Returning wide restores the initial allocation. The natural boundary request still needs15 native pixels of horizontal extent at96 DPI because the visible vertical scrollbar consumes client width; this is required scrolling, not stale extent.
- Geometry remains unchanged in every quiet observation window. Observed quiet-window size callbacks:0; fit callbacks:0. Normal resize callbacks occur while resizing.
- AMS zoom remains1 and setter calls remain0 in every phase, including the shown panels and height growth.

## Preservation, limits and reproduction

All 1766 original files have identical SHA-256, size and mtime before/after. This includes the original72-process results, probe/scripts, provenance, private headers and six private archives. `original-before.json` and `original-after.json` retain the inventories. The root warm build outputs were never inspected or touched. Source/Git/index/refs/GitHub/installed app/profile/printer/user-desktop state was not mutated; no network or Bambu build was performed.

This is native wxGTK on private Xvfb, not native Cocoa/MSW or full Bambu. Title, playbar, progress and Control rows have fixed synthetic minima; hidden AMS uses the short compact profile. Shown AMS replaces the rack with a fixed586×340 DIP panel and is taller than the hidden case. No actual WebView/DOM, backend readiness, asynchronous report schedule, printer, stream decoding or fullscreen lifecycle is exercised. Media returns invalid size so the actual production16:9 fallback runs. The fixture binds size events and defers the helper with CallAfter; full application event wiring is not compiled.

Settling means unchanged geometry and no size/fit callbacks during200ms nominal quiet observation after300ms nominal event pumping. This is finite observation, not a claim about every future event or all wx idle events. The previous negative control was not rerun and is not included in these counts. Non-wx GTK/system sysroot headers/shared libraries were reused read-only from the recorded original dependency paths.

Run `python3 build.py`, `python3 run.py`, then `python3 verify.py` from this directory. `COMMANDS.md` explains extraction/recreation and private-display isolation; `compile-command.json`, `xvfb-command.json` and `run-commands.json` retain exact commands. `results.json`, `findings.json`, `inputs.json`, `artifact-hashes.json`, per-case TSV/stderr and `raw-results.json` retain assertions, hashes and raw evidence.
