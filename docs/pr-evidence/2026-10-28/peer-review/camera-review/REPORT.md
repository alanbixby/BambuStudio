# camera_fable round 3 — PR10 `fix/camera-ams-balance`

Reviewed head `df28193c8e4aa5f2439f81eed83caa842a01c5ea` on master `79df7ae309be398ed30c9f397c13c9911c2edc57` (round-two head `6e81cd8f`, round-one head `6d4ff325`). Combined application `e79eb4721427ac7f136d6d5c5fa0acd962f57f30`, wx `3fea0af433d9630f79eaf8fbfc062364ba456be3`. Read-only; outputs only in this directory.

**Open blocking findings: 0.** CF-09 is fixed. Two non-blocking observations (CF-10, CF-11) are recorded for acceptance.

## Delta check

`git diff 6e81cd8f df28193c` touches only `src/slic3r/GUI/DeviceWeb/DeviceWebHost.cpp` (5+/3-), equal to `round3/camera-delta.patch`. The blob `0db7cf8f` is identical in the head and in combined `e79eb472`; the exported `bambu-10-camera-ams-balance.patch` equals `git diff base..head`. The fit solver in combined `StatusPanel.cpp` is byte-identical to the head's. The readiness gate (`:617`), macOS exclusions (`DeviceWebHost.cpp:611`, `StatusPanel.cpp:2077,2169`), fullscreen refit and comment corrections are unchanged from round two.

## CF-09 verification

Source: `SetAmsControlWebFitZoom` (`:656-665`) now resets the jitter baseline and calls `ApplyAmsControlWebHostSize` with the last reported height or `kAmsControlWebInitialHeightDip` (340, inside the 220..360 clamp at `:604-606`). `Apply` sets the panel min size to `lround(FromDIP(340)*z)` through the synchronous handler, so `GetBaseHeight() = lround(min/z)` divides a height that was actually scaled by `m_fit_zoom`.

Model (`pending_zoom_model_r3.py`, run with `python3 -I`): host state machine and the unchanged solver, 168 cases at scale 1.0/1.5/2.0, four window classes, page heights 220/260/300/336/340/344/360, backend ready at once (GTK) or after three fit passes (Edge).

- Pre-report passes produce exactly one zoom value in every case (no drift). The old `6e81cd8f` path in the same model reproduces 1.6 → 2.0 → 2.0 → 1.6.
- Zero zoom API calls while the backend is unready; the first ready report applies the pending zoom before the jitter return.
- `lround(lround(FromDIP(340)*z)/z) == FromDIP(340)` for every 5% step 1.00..2.00 at scales 1.0, 1.25, 1.5, 1.75, 2.0.
- After the first real report the final zoom equals the report-first reference except the CF-10 cases.

State assumptions checked: `m_last_logical_content_size` has no consumer besides the three AMS sites (the header comment about rebuilding on show has no code behind it, baseline); `msw_rescale` is empty; nothing else writes the AMS panel min size; hide/suspend/show keeps host and panel state consistent; `m_ams_base_zoom` is read only when a live backend exists.

## Non-blocking observations

- **CF-10** (GTK/Windows): because the synthetic 340 seeds the baseline jitter filter, a first real report within 8 DIP of 340 after a pre-report zoom is absorbed. Result: ≤7 DIP gutter and a zoom one 5% step from the report-first value, then stable. The panel comment says 340 is the tallest stack, so no clipping. Accept; fixing needs extra state.
- **CF-11** (Windows only): the host is widened before WebView2 exists, so the page first lays out at 586·z CSS px at zoom 1; if its height depends on width, one over-zoom step occurs and is corrected by the report WebView2 sends after the zoom re-layout. GTK applies the zoom at widening time. Accept; optionally note the one-time reflow in the body.

## Prior findings

CF-01, CF-02, CF-04, CF-06 fixed and unchanged; CF-03, CF-05 conceded; CF-07, CF-08 documented; CF-09 fixed (above). IDs stable.

## Limits

No compilation or runtime on any OS; backend behaviour from pinned wx sources. The model reuses round-one panel-height assumptions. The content_size page script is not in the repository. The latest PR10 body found is `round2/bodies/bambu-pr-10.md`; it remains accurate for this head.
