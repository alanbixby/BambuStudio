# Reproduction

Run from `/tmp/bambu-polish-20261028/implementation/camera-split-native`:

```sh
python3 build.py
python3 run.py
python3 verify.py
```

The existing extracted source and probe are sufficient for reproduction. To recreate the extraction and fixture from the same immutable Git object and read-only original probe, first run `python3 prepare.py`. This snapshots the original directory inventory again; retain the delivered `original-before.json`/`original-after.json` as evidence for this completed run. Do not run any script from the original `camera-native` directory: its prepare/build/verify scripts refer to warm wx outputs which are now owned by the root build.

`prepare.py` reads `bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7:src/slic3r/GUI/StatusPanel.cpp` and `.hpp` via `git show`, extracts the entire function unchanged, and adapts only the disconnected fixture. `fixture.diff` shows those adaptations. It reads the original sealed private copies and their provenance, without opening the recorded warm source locations. No wx-config invocation occurs.

`compile-command.json` contains the exact compiler/linker argument vector. `build.py` runs it with private TMPDIR and XDG directories, disabled ccache, no inherited display/preload/custom include/library paths, no core dumps, and a 60-second timeout. `compile.log` and `compile-dependencies.d` preserve its outputs. `dependency-check.json` confirms neither compiler arguments nor compiler-discovered dependencies contain a deps-build path. Only the already sealed `camera-native/private-wx` wx headers/static archives are used. Non-wx GTK and system headers/shared libraries use the read-only sysroot paths recorded in the original compiler command.

`xvfb-command.json` contains the exact private Xvfb invocation and environment overrides. `run-commands.json` contains each actual probe argument vector and GDK scale. `run.py` removes inherited DISPLAY, WAYLAND_DISPLAY, XAUTHORITY, LD_PRELOAD and scaling overrides, starts a private `xvfb-run -a` display with private authorization, disables network listening and core dumps, and applies a 30-second timeout per probe. Private font/config/cache/temp files stay in this directory. Xvfb uses its normal ephemeral X socket; it does not connect to the user's desktop.

The six hidden-AMS cases cover DPI96/144/192 x GDK scale1/2. Two additional shown-but-unzoomed AMS cases cover DPI96/scale1 and DPI192/scale2. Every process records ten phases: wide2200, narrow1400, undersized1000, natural boundary1218, narrow1400, wide2200, height1100, height520, narrow1400, and an extra queued helper call at narrow1400. The regular height is520 DIP.

`verify.py` asserts natural Control minimum preservation, required undersize scrolling, no excess horizontal extent, restored wide geometry, camera width minimum enforcement, stable geometry, no quiet-window size/fit callbacks, zero AMS zoom setter calls, zoom1, expected native DPI/scale metadata, exact process/phase counts, and unchanged contents/size/mtime for all original files. It reads only the sealed private archives when checking archive identity. It never reads or checks warm archives.

`inputs.json` holds exact source/function/fixture/archive hashes and each private wx header hash; `artifact-hashes.json` holds output/script hashes. Native per-run TSV and stderr files and `raw-results.json` are the underlying measurements. This focused run does not rerun or alter any of the previous72-process proof.
