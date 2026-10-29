# Validation notes for the focused PR series

The series now has sixteen focused candidates. Every candidate has one commit and fewer than 500 added/deleted lines. Camera fit and AMS zoom are separate; Project startup and native loading are independent. DPI unit corrections, progress layout and explicit GTK adoption form a review chain. Both wx changes are based on upstream `abb542694ef4534a50e65c5b877b2774d02952ae`.

The GTK sizing change is off by default. Corrected Bambu opts in at startup and pins an exact revision from the review fork. Old applications keep identity conversions unless they explicitly enable the option. Replace the temporary fork pin with the accepted upstream revision before submitting that integration upstream.

Project message ordering passes extracted-JavaScript scheduling checks; the previous source fails the same regression. The combined camera correction passes 72 private nativeGTK runs with 720 observations. The separate camera-only helper passes 8 runs with 80 observations. These fixtures use synthetic media and AMS panels, not a printer or WebView. Default-off/enabled conversion checks compile as C++98 with source doubles. A refreshed paired Linux build and actual-archive probes are in progress; no completed build result is claimed yet.

Windows/macOS have not been compiled or run. Source/API review, text merges and synthetic probes do not replace those checks. Screenshots on the PRs show earlier combined Linux builds. [Camera evidence correction](corrections.md) distinguishes older synthetic report schedules from production page behavior.

<a id="bambu-01"></a>

## bambu-01: Fix crash when returning from the Assembly view

3+ / 1- lines; 1 files. Base: `master`. Source: `f4218e246f3041077177d2487ce8824d522addfa`. [Patch](patches/bambu-01.patch).

<a id="bambu-02"></a>

## bambu-02: Keep the Assembly structure panel from covering the sidebar toggle

10+ / 2- lines; 3 files. Base: `master`. Source: `3ba2657c70ef031d011da175a4daafb850e3b3b1`. [Patch](patches/bambu-02.patch).

<a id="bambu-03"></a>

## bambu-03: Show Project information without waiting for the network lookup

254+ / 161- lines; 4 files. Base: `master`. Source: `ed5e975a59ee28242f67ded5e0722b19b61e0ed4`. [Patch](patches/bambu-03.patch).

<a id="bambu-04"></a>

## bambu-04: Fix dark-mode Project text colors and overlapping imported tables

32+ / 0- lines; 2 files. Base: `master`. Source: `44fa2692b16919f4519595d6bcd4f571777ea1d6`. [Patch](patches/bambu-04.patch).

<a id="bambu-05"></a>

## bambu-05: Fix double DPI scaling of icons, fonts and measured sizes

66+ / 63- lines; 18 files. Base: `master`. Source: `305b41867feec57eb3d535d59920a9f091991762`. [Patch](patches/bambu-05.patch).

<a id="bambu-06"></a>

## bambu-06: Wrap Print Options descriptions instead of cutting them off

67+ / 71- lines; 2 files. Base: `master`. Source: `2604e8279cf03f0ac93b53205608a7d901aacfc4`. [Patch](patches/bambu-06.patch).

<a id="bambu-07"></a>

## bambu-07: Let single-value settings fields use spare panel width

64+ / 1- lines; 3 files. Base: `master`. Source: `9df1217e47951f34cd95c65159f5329c88083c75`. [Patch](patches/bambu-07.patch).

<a id="bambu-08"></a>

## bambu-08: Even out printer and plate cards and align header buttons

21+ / 8- lines; 1 files. Base: `master`. Source: `5d431fccc52f0011f0613a74d224e81bc614d23f`. [Patch](patches/bambu-08.patch).

<a id="bambu-09"></a>

## bambu-09: Close the gap between temperature values and their unit

80+ / 21- lines; 2 files. Base: `master`. Source: `fc074b0ad0a55945fefcf16fe0b195a48d20e398`. [Patch](patches/bambu-09.patch).

<a id="bambu-10"></a>

## bambu-10: Fit the live camera to its video aspect ratio

49+ / 0- lines; 2 files. Base: `master`. Source: `bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7`. [Patch](patches/bambu-10.patch).

<a id="bambu-project-startup"></a>

## bambu-project-startup: Retry Project details until the page is ready

40+ / 3- lines; 1 files. Base: `master`. Source: `a2edccd9347f53d719984fd2997ce23155ee79a6`. [Patch](patches/bambu-project-startup.patch).

<a id="bambu-progress"></a>

## bambu-progress: Keep progress text and long messages from being clipped

9+ / 10- lines; 2 files. Base: `fix/native-dip-geometry`. Source: `5608a478ca983cc63083627bb6f8854f575412db`. [Patch](patches/bambu-progress.patch).

<a id="bambu-ams-zoom"></a>

## bambu-ams-zoom: Scale AMS to use spare room beside the camera

183+ / 12- lines; 6 files. Base: `fix/camera-ams-balance`. Source: `54083d6fb80138c3404a58abc2c4300c0035dfd7`. [Patch](patches/bambu-ams-zoom.patch).

<a id="bambu-gtk-integration"></a>

## bambu-gtk-integration: Use a pinned wx build for GTK font sizing

7+ / 2- lines; 2 files. Base: `fix/progress-text-layout`. Source: `e77253cd2ff240df00890d2e798faa312df23e95`. [Patch](patches/bambu-gtk-integration.patch).

<a id="wx-01"></a>

## wx-01: Measure GTK labels after their font changes

24+ / 0- lines; 1 files. Base: `master`. Source: `14a14a773c74ae23281417f58334b5c28ecfed12`. [Patch](patches/wx-01.patch).

<a id="wx-02"></a>

## wx-02: Allow apps to opt into GTK font-DPI sizing

91+ / 3- lines; 4 files. Base: `master`. Source: `d54f3313028fc439cea91f0b6a213e5ad2245b90`. [Patch](patches/wx-02.patch).

