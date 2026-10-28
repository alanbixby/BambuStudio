# WXO-2: rejected by actual WebKitGTK rendering

**Verdict: REJECTED for the installed GTK 3.24.41 / WebKitGTK 4.1 API, runtime 2.52.6.** WebKit already incorporates the forced GTK font DPI into the CSS-to-device scale at its default page zoom of 1.0. The pinned Home host's `FromDIP(224)` and `FromDIP(64)` allocations expose 224 and 64 CSS px respectively at every tested font DPI and integer window scale. There is no excess host width of the proposed kind. No production patch is warranted.

All investigation files are in this directory. App source `53fdfb67ed5272f6547a995d8bc0d19e9f37de6e` and wx source `292aae41bef6544ebd7c43096c8f7ce683c4f3fb` were read with `git show`; neither checkout was changed. No Bambu instance, installed application, desktop configuration, printer, login, camera, remote page, or GitHub action was used. The native probe used inline synthetic HTML, an ephemeral WebKit context, isolated HOME/XDG directories, and private Xvfb with TCP disabled. Native Xvfb necessarily creates its own temporary X11 socket/lock. No desktop display or user profile was opened.

## Measured default behavior

The host allocation below is in GTK/wx **user coordinates**. The native X window and WebKit snapshot dimensions are **physical pixels**. `innerWidth`, `getBoundingClientRect`, and computed style values are **CSS px**. These units must not be conflated.

| GDK scale | Forced font DPI | GTK host width for 224 CSS px | Native/snapshot width, physical px | `innerWidth`, CSS px | `devicePixelRatio` | Rendered 32-CSS-px marker, physical px |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 96 | 224 | 224 | 224 | 1 | 32 |
| 1 | 144 | 336 | 336 | 224 | 1.5 | 48 |
| 1 | 192 | 448 | 448 | 224 | 2 | 64 |
| 2 | 96 | 224 | 448 | 224 | 2 | 64 |
| 2 | 144 | 336 | 672 | 224 | 3 | 96 |
| 2 | 192 | 448 | 896 | 224 | 4 | 128 |

All rows use WebKit page zoom **1.0**, full-content zoom mode, and GDK_DPI_SCALE=1. `gtk-xft-dpi` was explicitly assigned 96/144/192 times 1024 before creating the WebKit context, and the probe recorded the effective `gdk_screen_get_resolution` for every sample. These are forced-setting experiments, not desktop XSettings normalization tests.

At both GDK scales, collapsed host allocations of 64/96/128 GTK user units expose **64 CSS px** at font DPI 96/144/192. Generic host allocations of 560/840/1120 GTK user units expose **560 CSS px**. The fixture's `max-width:168px` media query selects the compact menu only for the intended collapsed widths.

With a fixed **224 GTK user-unit** allocation instead of FromDIP, the default viewport shrinks to `innerWidth=149` at 144 DPI and `112` at 192 DPI. At 144 DPI its fractional `visualViewport.width` is 149.333328 CSS px; integer `innerWidth` truncates. The fixture incorrectly enters the compact menu breakpoint at these fixed allocations. Skipping FromDIP would therefore introduce a regression on this runtime.

## Why computed fonts do not reveal the physical scaling

The fixture records a `16px` declaration, a `12pt` declaration, and an unspecified default font. All three computed sizes remain **16 CSS px** across the entire matrix; WebKit's default font-size setting also remains 16. The 224-CSS-px red block, 32-CSS-px blue marker and 24-CSS-px menu icon retain their CSS dimensions. Their rendered physical dimensions scale with font DPI and integer GDK scale. Thus unchanged CSS font sizes do **not** imply unchanged physical rendering.

The canvas has explicit intrinsic attributes 32×16 and CSS dimensions 32×16. Its author-controlled backing attributes stay 32×16. WebKit's full-view snapshot backing dimensions and native X geometry do scale. The returned snapshot is an already-physical BGRA image whose Cairo surface device-scale metadata is 1, including at GDK scale 2. Canvas attributes and that Cairo metadata are not evidence that the browser ignores DPI.

Measured relationship in this setup, where F = effective GTK font DPI / 96, S = integer GDK scale, and Z = explicit WebKit page zoom:

- One CSS px maps to F × Z GTK user units and F × Z × S physical pixels.
- `devicePixelRatio` is F × Z × S.
- Viewport CSS width is host GTK user width / (F × Z).
- Native host physical width is host GTK user width × S.

These relationships are conclusions checked against DOM measurements, actual BGRA raster color runs, and native XGetGeometry values; they are not arithmetic-only rendering evidence.

## Proposed zoom correction would double-scale

The probe also explicitly applied the suggested `FromDIP(100)/100.0` page zoom while keeping the matching FromDIP host widths:

| Font DPI | Explicit page zoom | Host GTK width | Resulting `innerWidth`, CSS px | 32-CSS-px marker at GDK scale 1, physical px |
|---:|---:|---:|---:|---:|
| 144 | 1.5 | 336 | 149 | 72 |
| 192 | 2 | 448 | 112 | 128 |

This introduces a second font-DPI factor. The nominal expanded menu becomes compact under the fixture's 168-CSS-px breakpoint. The 64 and 560 CSS-px host tests likewise shrink their CSS viewports by another factor of 1.5 or 2. GDK scale 2 doubles physical raster widths but does not alter the resulting CSS viewport widths.

Examples inspected visually: `gdk1-dpi144/fromdip224-default.png` and `gdk1-dpi144/fromdip224-fontzoom.png`. The former shows the expected expanded menu; the latter has oversized contents and the compact breakpoint. These are synthetic test pages, not the actual Home UI.

## Pinned source and installed API evidence

`source-evidence.txt` records numbered excerpts read from the immutable commits and installed headers/GIR documentation. `provenance.json` records complete commit IDs, package versions and runtime library SHA-256 hashes. `linked-libraries.txt` confirms the probe loads the installed system GTK/WebKit libraries rather than an alternate sysroot runtime.

- App `WebViewDialog.cpp:241–243,2484–2488` uses FromDIP for initial and JS-reported Home menu widths. `homepage3/js/left.js:333–354` reports 224/64 and compares `window.innerWidth` with 168. `left.html:14` uses the same CSS media-query boundary. `left.css` sets CSS font/icon dimensions and makes the menu board fill its viewport; the hypothesized visual problem would be excess space around unchanged-size content, not necessarily a literal empty fixed-width board.
- wx `src/gtk/window.cpp:4391–4412` derives DIP scale from effective GDK screen font resolution divided by 96. Its GTK content scale remains the separate integer widget scale. The probe supplies known host allocations matching this pinned conversion; it does not link or run the full wx archive.
- wx `src/gtk/webview_webkit2.cpp:654,744–751,1033–1047` creates the native WebKit view and directly exposes page zoom and full-content/text-only zoom. Absence of a wx DPI-specific `SetZoomFactor` call does not imply WebKit lacks internal DPI scaling.
- Installed WebKit2-4.1 GIR, derived from the actual library source, documents default page zoom 1.0, default font size 16 pixels, `zoom-text-only=false`, the asynchronous JavaScript API and BGRA8888 snapshot API. Headers provide those declarations. The installed WebKit binary also contains `notify::gtk-xft-dpi`; that string is corroboration of integration, not proof of its full internal implementation. Full WebKit implementation source was not present locally; the behavioral verdict rests on the real native rendering experiment.

The original finding's proposed verification heuristic is reversed/misleading: at 144 DPI a **336 GTK-user-unit host / 224 CSS-px viewport = 1.5** is the correct matching conversion, not evidence of excess width. Excess width would require the viewport to expose 336 CSS px while the intended content width is 224. The probe measures 224.

## Recommendation and limits

Retain the existing FromDIP Home/generic host sizing. Add no font-DPI zoom compensation and do not special-case GTK to bypass FromDIP. Existing AMS fit zoom is a separate responsive fit mechanism; this result does not require changing it.

The generic DeviceWebHost comment at `DeviceWebHost.cpp:681–683` calls wx SetMinSize coordinates “physical pixels.” That wording is inaccurate on GTK at integer scale 2. A documentation-only replacement can say: “The page reports CSS-pixel dimensions. Convert them to wx window coordinates; GTK applies its integer content scale when rendering.” There is no demonstrated sizing bug to fix here. This investigation produced no production patch.

Scope is private X11/Xvfb, GTK 3.24.41, WebKitGTK runtime 2.52.6, explicit font settings, scale 1/2 and default zoom. It does not establish older WebKit versions, Wayland, real desktop normalization, live DPI changes after initialization, macOS, Windows, or full Bambu Home integration. Those limits do not weaken rejection of WXO-2 for the installed Linux runtime tested here.

## Reproduction

From this directory:

```sh
bash build.sh
bash run.sh
python3 check.py
```

One compiler process builds one translation unit. Each matrix pass has six independent private Xvfb runs and seven sequential rendered states per run, producing 42 snapshots. The matrix was executed twice; the final pass has clean per-run JSONL measurements and separate diagnostic logs. `check.py` validates CSS/native/raster consistency, the 224/64/560 viewport widths, default font behavior, and the adverse result of the proposed extra zoom; it exports `matrix.csv` and `matrix.json`. `validation.txt` contains the final check result.
