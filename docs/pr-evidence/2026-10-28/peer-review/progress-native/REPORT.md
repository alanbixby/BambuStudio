# ProgressDialog two-edit native follow-up

**Pass for the requested initial/parent correction.** All 348 follow-up rows excluding the separately retained unbreakable-name case pass. Initially short and initially-long creation, short→long→short, wrap-boundary messages and final-line reachability pass at font DPI 96/144/192, GDK_SCALE 1/2, on both tested native themes. The actual production override and initialization statements are extracted from the tested source, with no surrogate parent sizing branch.

**The known unbreakable-name failure remains red:** 24 cases fail native label-height and horizontal-containment checks. Including these cases makes full verification exit 1. There are no other follow-up failing rows. This is not a claim that every ProgressDialog input is green.

Application commit `24d91027fb6d07bbffac558afbeba699292e653a` has ProgressDialog.cpp SHA-256 `91625271dfa5761e8b307516b9ff21456c23b4f92181a35cfed12cf5b809aea8`, byte-identical to the prepared follow-up candidate. `patch-application.json` proves the private application differs from the prior candidate by exactly the two requested edits. The resize override delegates to wxDialog::DoSetSize, and initial FormatString occurs immediately after SetSizer, before Layout/Fit/Centre.

Both compared candidates link the same private copies of wx `3fea0af433d9630f79eaf8fbfc062364ba456be3`. Copies were taken only after the stable-archive notice. Core SHA-256 is `53da679b427c37a72300985c81c7f779182d32066fe9881a4812ee76dccedc7a`; base is `d281166b58c5f8e7128292e731f5b5983641599ea3ebf7b670f3e0c3859a81c1`. Both match the supplied notice. Six static archives and 1495 wx headers were copied privately; no warm archive is used as a link input. One compiler job, exit 0, empty compile.log. Private archives remain byte-identical after testing.

There are 48 final native process launches and 744 measurement rows across prior/follow-up, short/long initialization, six DPI/scale combinations and two themes. Every process exits 0. The prior candidate reproduces its initial allocation failures at 144/192 DPI. All 315 old evidence files remain byte-identical, checked against the complete pre-follow-up hash manifest; no old evidence was rewritten.

Representative follow-up initial geometry under Adwaita is below. GDK_SCALE 2 gives the same logical pixel results. Native top-level allocation is recorded in each stderr file; at 144 DPI it is 592×394, rather than the prior 400×250 cap.

| Font DPI | Initial content | Wrap width | Actual client | Label height | Virtual height | Max scroll px |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| 96 | short | 325 | 330×150 | 17 | 150 | 0 |
| 96 | long | 325 | 330×150 | 1717 | 1717 | 1570 |
| 144 | short | 485 | 493×225 | 24 | 225 | 0 |
| 144 | long | 485 | 493×225 | 2424 | 2424 | 2200 |
| 192 | short | 645 | 655×300 | 32 | 300 | 0 |
| 192 | long | 645 | 655×300 | 3232 | 3232 | 2935 |

The second theme adds wxBORDER_SIMPLE and uses a wider scrollbar with 7-pixel spacing. It keeps the production FormatString statements unchanged, and still passes all non-unbreakable initial/update rows. All final rows assert native overlay scrolling is disabled. Native border/scrollbar metrics, Pango text bottom, label and virtual dimensions, adjustment range/page, and maximum scroll are in the TSV files.

Commands, from this directory:

```sh
python3 copy-archives.py
python3 build.py
python3 run.py
PROGRESS_BORDER_STRESS=1 python3 run.py
python3 verify.py
python3 verify.py --include-known-unbreakable
```

The copy step requires a stable installed prefix; it was run after the supplied notice. Complete compiler argv is in compile-command.json and shell form in compile-command.sh. Xvfb commands and environment overrides are in xvfb-command*.json; native commands are in run-commands*.json. The final verify command intentionally exits 1 for the known filename issue. `manifest.json` records hashes, source identity, counts, representative geometry, commands and verdicts.

The native test uses only private xvfb-run servers, with desktop DISPLAY/WAYLAND_DISPLAY/XAUTHORITY removed before launch. Fonts, XDG data/cache/runtime, compiler temporaries and outputs are scoped to this new directory. Standard Xvfb sockets/locks are transient server artifacts. No input injection, Studio launch, printer communication, existing process attachment, production edit or build-cache write was performed by this probe.

The dialog shell omits GUI_App/main-frame parenting, dark-mode initialization, modal disabling, custom cancel buttons and progress lifecycle. The adaptive label/scroller/sizer, both initialization sequences and override bodies are real extracted statements. The tested no-cancel branch leaves the cancel pointer null. This does not exercise non-adaptive dialogs, decorated dialogs under a window manager, cancellation callbacks, live DPI changes or full Studio integration.

Frozen native-source interpretation is in SOURCE-INTERPRETATION.md: GTK now reaches wxTopLevelWindowGTK::DoSetSize and gtk_window_resize; Windows/macOS resolve to the same resize implementation reached by the old call. No specific source-level cross-OS blocker was found. Windows/macOS were not compiled or run. The GTK native resize and size-event effects are intended changes and apply beyond the adaptive branch; those broader runtime paths remain untested.
