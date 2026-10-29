# GTK3 font-DPI opt-in candidate

Candidate complete. No new blocking flaw was found in this compatibility seam. All changes are unapplied patches and scratch copies. No repository, index, ref, installed application, profile, GUI or printer was changed; no delegation, project build, network request or publication was performed.

**Open candidate blocking count: 0.** The inherited **WXSOL-001 integration gate remains open** until the parent integrates the patches and selects the resulting exact wx revision in Bambu's dependency recipe. This report does not close the broader integration finding or approve the stack for merging.

## Exact inputs and patch size

| Project | Exact input head | Candidate diff |
| --- | --- | --- |
| wx | `3fea0af433d9630f79eaf8fbfc062364ba456be3` | 13 added / 3 removed; 3 files |
| Bambu | `0b34fcad456618e5d023e4f475dffb3f75ae6472` | 5 added / 0 removed; 1 file |

Sources were read with `git show SHA:path`, independently of the working trees. `prepare-commands.json` records these commands and source SHA-256 digests. Source snapshots are in `original/`, proposed full files in `candidate/`. `source-manifest.json` records exact SHA-256 and Git blob IDs. The older app head `1f880d3c` is not the app patch base.

The wx patch touches only `src/gtk/window.cpp`, `interface/wx/window.h` and `interface/wx/sysopt.h`. The app patch touches only `src/slic3r/GUI/GUI_App.cpp`. `include/wx/window.h` and wx1 implementation files are untouched.

## Behavior and policy

At candidate wx `src/gtk/window.cpp:4394`, `wxGTKDIPScale()` returns 1 unless `wxSystemOptions::GetOptionInt("gtk.window.font-dpi-scaling")` returns exactly 1. This check precedes the window handle, GDK screen and GTK settings accesses. Both size conversions already return their input immediately for scale 1. The existing point/scalar/member wrappers therefore preserve identity too, including -1, zero, other signed coordinates and integer limits.

Unset options return zero through the existing system-options implementation. With `wxUSE_SYSTEM_OPTIONS=0`, the actual frozen `include/wx/sysopt.h:59` accessor stub returns zero. No extra conditional, API, parser, build option or scale cache was added. The existing system-options environment mechanism also remains available: an explicit option environment setting can opt an older app in. This is default-off compatibility, not a prohibition on deliberate external opt-in. Bambu's explicit SetOption takes precedence over environment settings through the existing wx option implementation.

When enabled, deleting only the four added guard lines makes the entire wx executable source byte-identical to the frozen input. DPI acquisition, fallback, rounding, -1/zero handling, signed-coordinate rules and saturation are unchanged. DPI and screen changes are still read on each conversion. The new wx code remains within the existing `__WXGTK3__` block; it changes no Windows, macOS or GTK2 conversion path.

At candidate Bambu `GUI_App.cpp:2911`, the option is set at the beginning of `GUI_App::OnInit()`, guarded by `#if defined(__WXGTK3__) && wxUSE_SYSTEM_OPTIONS`. This precedes the call to `on_init_inner()` at 2919. That startup routine contains the Linux data-directory dialog check at 3219, TLS `RichMessageDialog` at 3282, splash creation at 3397, preset bundle creation at 3413 and main-frame creation at 3624. The later replacement main-frame site at 4445 is unchanged. These are source/call-site checks; the startup probe uses a simulated inner routine. This is not a runtime trace of every possible callback before OnInit.

The existing system-option flag table documents the GTK3-only option, default identity behavior and the requirement to set it before creating windows and keep it unchanged afterwards. The FromDIP documentation now states the opt-in condition.

## Checks and results

Run `python3 prepare.py`, then `python3 verify.py` from this directory to reproduce. The scripts write only here. Compiler temporary files use this directory's `tmp/`; compilation calls g++ directly with caching disabled. No project build or warm archive/cache is used.

`test-commands.json` records every verification command, working directory, output and exit status. Both conversion variants and all startup variants compiled with GCC 13.3.0 using `-std=c++98 -pedantic-errors -Wall -Wextra -Werror -O0 -g -fsanitize=undefined -fno-sanitize-recover=all`. All expected-success commands returned 0, with no UBSan diagnostics.

- Options enabled: **4,582,484 probe assertions passed**. Off values were 0, -1, 2, INT_MIN and INT_MAX. Every FromDIP/ToDIP overload was checked for identity with null, valid and handle-less window doubles; no window/GDK/settings calls occurred. Inputs include a signed interval and edge combinations, rather than every possible integer.
- Enabled conversions matched the separately extracted frozen baseline at font DPI 48/72/96/120/144/192/288 and invalid/extreme DPI values. Explicit checks covered saturation, sentinels, positive/negative results, DPI changes, different window/default screens and missing screens. The byte comparison also confirms that all enabled-path arithmetic is untouched.
- Options disabled: **271,184 probe assertions passed** using the actual frozen `wx/sysopt.h` and its zero stub. Even an attempted test option value of 1 stayed off, without state reads. Supporting wxObject/wxString types were doubles.
- Red control: the frozen unguarded implementation deliberately failed the default-off/no-state-read requirement with exit 1 and `FAIL: window/GDK state accessed while option was off`. See `red-control.txt`.
- The extracted Bambu startup prefix compiled and ran in GTK3/options-on, GTK3/options-off, GTK2, Windows-macro and macOS-macro configurations. Only GTK3/options-on called SetOption, before simulated inner startup. These are Linux-host macro/stub probes, **not Windows/macOS compilation**.
- The exact guarded wx block compiled and ran with no GTK/wx declarations when `__WXGTK3__` was absent, confirming the preprocessing boundary.
- Both patches passed `git apply --check`, applied byte-for-byte to the candidates, passed reverse checks and reversed byte-for-byte to the original inputs. All applies were confined to `applied/` scratch copies.

`verification.json` contains the structured results. `extractions.json` records extracted source spans and hashes. The assertion counts include stub instrumentation; they do not describe native GUI test cases.

## Integration still owned by parent

The app input still selects `https://github.com/bambulab/wxWidgets` with `GIT_TAG master` in `deps/wxWidgets/wxWidgets.cmake:27-28`. Applying the app option alone therefore does not select this wx implementation. After integrating the wx gate on the intended base, the parent must pin an exact reachable wx SHA containing wx1, wx2, this gate and the intended upstream changes, using the correct repository URL. Keep the app integration PR stacked on the corrected consumers. No dependency-recipe patch is supplied here.

The read-only upstream-context comparison found no differences in the five listed GTK/interface/header files between wx frozen upstream `e2fa9bda52f720242e35def30ac4a01fbe75f5a8` and current upstream `abb542694ef4534a50e65c5b877b2774d02952ae`; see `integration-context.json`. This candidate is nevertheless based on `3fea0af4`, not a newly created rebased commit.

Native verification remains the parent's integration task: rebuild the selected wx plus corrected Bambu and exercise GTK3 font DPI 96/144 and GDK scale 1/2, including an older unopted consumer and the corrected opted-in startup. No Linux GUI was launched. Windows/macOS, GTK2 and full wx/system-options-disabled configurations were not natively built or run. No shared-library/ABI or all-OS/merge-readiness claim is made. Full system-option string/environment behavior was read in exact source, not executed by the enabled-options double. Any existing limitations in the enabled conversion algorithm are inherited; this patch preserves that path.

## Artifact hashes

- `wx-opt-in.patch`: `94e65a5e7d8c1e6e99b3bc4f39565ddc6e9f0438f67ded78d017cd1493b697a9`
- `app-opt-in.patch`: `69dc6eb82bff0e8018f8e948b3b2ac8a5fd648bd48a253a7aab207a18f98e43d`

`artifact-hashes.sha256` records every delivered file, including this report, probes, executables and test outputs, except that manifest itself. Check it with `sha256sum -c artifact-hashes.sha256` from this directory. `findings.json` distinguishes zero new candidate blockers from the inherited parent integration gate.
