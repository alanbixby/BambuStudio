# Validation notes for the focused PR series

Sixteen one-commit candidates, each below 500 added/deleted lines. Project page startup and native loading are independent. Camera fit and AMS zoom are separate. Mechanical DPI, progress layout and explicit GTK adoption form a small review chain. Assembly clearance is independent of Assembly return. Both wx changes are based on upstream `abb542694ef4534a50e65c5b877b2774d02952ae`.

GTK font-DPI sizing is off by default. Corrected Bambu opts in at startup and pins `0f2037facedf3d92660e7071b6754fe994aa744d`. Replace the temporary fork URL/SHA with the accepted official revision before upstream adoption. Older apps keep their current default conversions.

The Linux warm build passed for app `e9617d1a815183350bd9822fb894996aa086f47a` and that wx pair. All product source was checked; six local CMake adaptations are disclosed. Actual native archive tests cover default-off/enabled, bounds, dynamic DPI and label fonts; a separate complete system-options-disabled wx build passes. [Build record](build/REPORT.md). Source-extracted Project scheduling checks reproduce the old link-order failure and pass on the correction. Native GTK camera fixtures verify width contraction and required scrolling, using synthetic controls rather than real video/WebViews.

Windows/macOS have not been compiled or run; the polished Studio bundle was not launched or installed. Screenshots are earlier Linux evidence, with shared-context and isolated-capture gaps disclosed in each draft. [Camera evidence correction](corrections.md) qualifies older stress-model assumptions. The existing installed bundle remains unchanged.

Fourteen reviews completed across Opus, Fable, Sol and Astra. No blocking objection remains in any partition. The three-round cap was respected. Minor requested wording changes after the cap were checked by the parent. [Review summary](review-summary.json).

[Parent decisions and limits](parent-responses.md). Review reports below retain their exact historical inputs; only two candidate heads changed after round2, moving one comment without altering the combined source tree. Final draft titles, bases, one-commit counts and substantive wording were read back; GitHub reports all 16 mergeable, with no workflow check runs or commit statuses. This is not CI success. Validation links move to this immutable snapshot after publication. [Exact final composition](final-composition-check.json).

round1: [camera_temperature_astra](round1/camera_temperature_astra/REPORT.md), [design_scope_opus](round1/design_scope_opus/REPORT.md), [editorial_fable](round1/editorial_fable/REPORT.md), [native_sol](round1/native_sol/REPORT.md), [project_astra](round1/project_astra/REPORT.md), [wx_sol](round1/wx_sol/REPORT.md).

round2: [camera_temperature_astra](round2/camera_temperature_astra/REPORT.md), [design_scope_opus](round2/design_scope_opus/REPORT.md), [editorial_fable](round2/editorial_fable/REPORT.md), [native_sol](round2/native_sol/REPORT.md), [project_astra](round2/project_astra/REPORT.md), [wx_sol](round2/wx_sol/REPORT.md).

round3: [design_scope_opus](round3/design_scope_opus/REPORT.md), [editorial_fable](round3/editorial_fable/REPORT.md).


<a id="bambu-01"></a>

## bambu-01: Fix crash when returning from the Assembly view

[Draft #1](https://github.com/alanbixby/BambuStudio/pull/1).

3+ / 1- lines; 1 files. Base: `master`. Source: `f4218e246f3041077177d2487ce8824d522addfa`. [Patch](patches/bambu-01.patch).

<a id="bambu-02"></a>

## bambu-02: Keep the Assembly structure panel from covering the sidebar toggle

[Draft #2](https://github.com/alanbixby/BambuStudio/pull/2).

10+ / 2- lines; 3 files. Base: `master`. Source: `3ba2657c70ef031d011da175a4daafb850e3b3b1`. [Patch](patches/bambu-02.patch).

<a id="bambu-03"></a>

## bambu-03: Show Project information without waiting for the network lookup

[Draft #3](https://github.com/alanbixby/BambuStudio/pull/3).

254+ / 161- lines; 4 files. Base: `master`. Source: `ed5e975a59ee28242f67ded5e0722b19b61e0ed4`. [Patch](patches/bambu-03.patch).

<a id="bambu-04"></a>

## bambu-04: Fix dark-mode Project text colors and overlapping imported tables

[Draft #4](https://github.com/alanbixby/BambuStudio/pull/4).

32+ / 0- lines; 2 files. Base: `master`. Source: `44fa2692b16919f4519595d6bcd4f571777ea1d6`. [Patch](patches/bambu-04.patch).

<a id="bambu-05"></a>

## bambu-05: Fix double DPI scaling of icons, fonts and measured sizes

[Draft #5](https://github.com/alanbixby/BambuStudio/pull/5).

66+ / 63- lines; 18 files. Base: `master`. Source: `305b41867feec57eb3d535d59920a9f091991762`. [Patch](patches/bambu-05.patch).

<a id="bambu-06"></a>

## bambu-06: Wrap Print Options descriptions instead of cutting them off

[Draft #6](https://github.com/alanbixby/BambuStudio/pull/6).

67+ / 71- lines; 2 files. Base: `master`. Source: `2604e8279cf03f0ac93b53205608a7d901aacfc4`. [Patch](patches/bambu-06.patch).

<a id="bambu-07"></a>

## bambu-07: Let single-value settings fields use spare panel width

[Draft #7](https://github.com/alanbixby/BambuStudio/pull/7).

64+ / 1- lines; 3 files. Base: `master`. Source: `9df1217e47951f34cd95c65159f5329c88083c75`. [Patch](patches/bambu-07.patch).

<a id="bambu-08"></a>

## bambu-08: Even out printer and plate cards and align header buttons

[Draft #8](https://github.com/alanbixby/BambuStudio/pull/8).

21+ / 8- lines; 1 files. Base: `master`. Source: `5d431fccc52f0011f0613a74d224e81bc614d23f`. [Patch](patches/bambu-08.patch).

<a id="bambu-09"></a>

## bambu-09: Close the gap between temperature values and their unit

[Draft #9](https://github.com/alanbixby/BambuStudio/pull/9).

80+ / 21- lines; 2 files. Base: `master`. Source: `fc074b0ad0a55945fefcf16fe0b195a48d20e398`. [Patch](patches/bambu-09.patch).

<a id="bambu-10"></a>

## bambu-10: Fit the live camera to its video aspect ratio

[Draft #10](https://github.com/alanbixby/BambuStudio/pull/10).

49+ / 0- lines; 2 files. Base: `master`. Source: `bed9f5a1fbab2ffb73cb5aea0dfc72a6e899a9d7`. [Patch](patches/bambu-10.patch).

<a id="bambu-project-startup"></a>

## bambu-project-startup: Retry Project details until the page is ready

[Draft #11](https://github.com/alanbixby/BambuStudio/pull/11).

40+ / 3- lines; 1 files. Base: `master`. Source: `a2edccd9347f53d719984fd2997ce23155ee79a6`. [Patch](patches/bambu-project-startup.patch).

<a id="bambu-progress"></a>

## bambu-progress: Keep progress text and long messages from being clipped

[Draft #12](https://github.com/alanbixby/BambuStudio/pull/12).

9+ / 10- lines; 2 files. Base: `fix/native-dip-geometry`. Source: `5608a478ca983cc63083627bb6f8854f575412db`. [Patch](patches/bambu-progress.patch).

<a id="bambu-ams-zoom"></a>

## bambu-ams-zoom: Scale AMS to use spare room beside the camera

[Draft #13](https://github.com/alanbixby/BambuStudio/pull/13).

181+ / 10- lines; 6 files. Base: `fix/camera-ams-balance`. Source: `a273fd21b1580662221037549e09bd7e10bcc615`. [Patch](patches/bambu-ams-zoom.patch).

<a id="bambu-gtk-integration"></a>

## bambu-gtk-integration: Use a pinned wx build for GTK font sizing

[Draft #14](https://github.com/alanbixby/BambuStudio/pull/14).

9+ / 4- lines; 3 files. Base: `fix/progress-text-layout`. Source: `74a75752f34633a5bb00d8a96bc6a30fc9a2744a`. [Patch](patches/bambu-gtk-integration.patch).

<a id="wx-01"></a>

## wx-01: Measure GTK labels after their font changes

[Draft #1](https://github.com/alanbixby/wxWidgets/pull/1).

24+ / 0- lines; 1 files. Base: `master`. Source: `14a14a773c74ae23281417f58334b5c28ecfed12`. [Patch](patches/wx-01.patch).

<a id="wx-02"></a>

## wx-02: Allow apps to opt into GTK font-DPI sizing

[Draft #2](https://github.com/alanbixby/wxWidgets/pull/2).

91+ / 3- lines; 4 files. Base: `master`. Source: `d54f3313028fc439cea91f0b6a213e5ad2245b90`. [Patch](patches/wx-02.patch).
