# Reproduction

Working directory for every command below:
`/tmp/bambu-polish-20261028/implementation/camera-native`

Read source with `git show HEAD:src/slic3r/GUI/StatusPanel.cpp`, where old head is `fab83eef842e6967fa06d0bb05410940b4787d28` and new head is `010ae25289256dda9f0d09111cf24c28bdf44394`. `prepare.py` performs these exact reads, extracts the entire function without editing it, and snapshots/hashes the read-only stable warm archives and headers into this directory. `combined-check.json` separately checks the exact function from `b7a379241d133f1808918aa9fc99caa1eeba3c79`.

Only rerun prepare after coordinating stable warm inputs with their owner; compare `provenance.json` before replacing it. All generated outputs, temporary compilation files, runtime configs and font caches are redirected here. Xvfb owns its normal ephemeral private-display Unix socket; no display/input calls target the user's desktop.

```sh
python3 prepare.py
python3 build.py
python3 compact.py
python3 build-compact.py
python3 ams-events.py
python3 build-ams-events.py
python3 run.py
python3 run-compact.py
python3 run-ams-events.py
python3 verify.py
```

The run scripts independently start `xvfb-run -a` with private authorization and pass only that server's DISPLAY and XAUTHORITY to the probes. Their environment first removes inherited DISPLAY/WAYLAND_DISPLAY/XAUTHORITY and scaling/preload overrides. They have 30-second per-process timeouts and disable core dumps. Builds are one compiler process at a time and link copied static archives, without application builds. `compile-commands*.json` preserve exact compiler/linker arguments. `xvfb-command*.json` and `run-commands*.json` preserve private-display commands and per-case scale/DPI/branch/height. GDK settings are changed only inside these short-lived processes.

Verification compares actual virtual/client/minimum sizes, camera minimum enforcement, required undersize scrolling, stable geometry, and absence of size/fit callbacks over the quiet observation window. It also verifies real zoom >1 is reached in AMS-event height-grow cases, exact negative-control excess survives an extra queued fit, and six warm archive hashes remain unchanged.

The initial AMS-events exploration used an incorrect stand-in constructor after introducing production-style GetBaseHeight readback; it set its initial height from an unset min. Those seven completed runs and one interrupted run are excluded and retained in `invalid-ams-initialization/`. The corrected fixture initializes 586x340 DIP directly as production does. The compiler probes and corrected full matrix pass/fail results are reported independently. Initial read-only path lookups for the AMS panel/host used two nonexistent paths; corrected immutable tree paths and the failed lookups are preserved in `supporting-sources.json`. One initial app diff used the wx repository by mistake and failed with `fatal: bad object`; the corrected exact app diff confirmed only the intended budget/FitInside function changes.
