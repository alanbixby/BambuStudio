void StatusBasePanel::fit_camera_to_feed()
{
    if (is_camera_fullscreen() || !m_media_ctrl || !m_machine_ctrl_panel || !m_control_rows_sizer || !m_camera_media_sizer)
        return;

    wxSizer *control_sizer = m_machine_ctrl_panel->GetSizer();
    wxSizer *camera_column = m_camera_media_sizer;
    wxSizerItem *camera_item = camera_column->GetItem(m_media_ctrl);
    if (!control_sizer || !camera_item)
        return;

    // The shown web AMS view, its size at zoom 1 and its current zoom.
    wxWindow *ams    = nullptr;
    int       base_w = 0;
    int       base_h = 0;
    double    current_zoom = 1;
#if BBL_ENABLE_AMS_CONTROL_WEB && !defined(__WXOSX__)
    // wx's macOS backend magnifies the view without changing its CSS layout.
    // Keep AMS unzoomed there; the camera aspect fit below still applies.
    if (m_ams_control_web_panel && m_ams_control_web_panel->IsShown()) {
        ams          = m_ams_control_web_panel;
        base_w       = m_ams_control_web_panel->GetBaseWidth();
        base_h       = m_ams_control_web_panel->GetBaseHeight();
        current_zoom = m_ams_control_web_panel->GetFitZoom();
    }
#endif

    // Natural Control width with AMS unzoomed, and the width AMS may fill.
    int rows_base  = m_control_rows_sizer->CalcMin().x;
    int ams_border = 0;
    if (ams) {
        rows_base = 0;
        for (wxSizerItem *item : m_control_rows_sizer->GetChildren()) {
            if (!item->IsShown())
                continue;
            const int border = item->GetMinSizeWithBorder().x - item->GetMinSize().x;
            int width = item->GetMinSizeWithBorder().x;
            if (item->GetWindow() == ams) {
                ams_border = border;
                width = base_w + border;
            }
            rows_base = std::max(rows_base, width);
        }
    }
    // A maximum cannot be adjusted by subtracting a zoomed child's width:
    // that loses a wider header when AMS becomes the largest child. Measure
    // each top-level item with the unzoomed row width instead.
    int natural = 0;
    for (wxSizerItem *item : control_sizer->GetChildren()) {
        if (!item->IsShown())
            continue;
        int width = item->GetMinSizeWithBorder().x;
        if (item->GetSizer() == m_control_rows_sizer)
            width = rows_base + width - item->GetMinSize().x;
        natural = std::max(natural, width);
    }

    // Whole 5% steps rounded down, so the result is reproducible and fits.
    auto zoom_step = [](double zoom) { return std::clamp(std::floor(zoom * 20 + 1e-6) / 20, 1.0, 2.0); };

    int    target = wxDefaultCoord;
    double zoom   = 1;
    const int row_width = m_media_ctrl->GetSize().x + m_machine_ctrl_panel->GetSize().x;
    const int column_h  = camera_column->GetSize().y;
    // Tallest feed the column offers.
    const int camera_h  = column_h - camera_column->CalcMin().y + camera_item->GetMinSizeWithBorder().y;
    if (m_media_ctrl->IsShown() && camera_h > 0 && row_width > 0) {
        wxSize video = m_media_ctrl->GetVideoSize();
        if (video.x <= 0 || video.y <= 0)
            video = wxSize(16, 9);
        const double aspect = double(video.x) / video.y;

        // Feed height to reach, and the Control width its zoom needs.
        double feed_h    = camera_h;
        int    control_w = natural;
        const int extra_w = natural - rows_base + ams_border;
        if (base_w > 0 && base_h > 0) {
            auto min_h = [camera_column](wxWindow *window) {
                wxSizerItem *item = camera_column->GetItem(window);
                return item && item->IsShown() ? item->GetMinSizeWithBorder().y : 0;
            };
            // Camera title and play bar, and the Control column without AMS.
            const int    chrome_h = min_h(m_panel_monitoring_title) + min_h(m_media_play_ctrl);
            const int    extra_h  = control_sizer->CalcMin().y - ams->GetMinSize().y;
            const double level    = (row_width - extra_w + aspect * (chrome_h - extra_h)) / (base_w + aspect * base_h);
            const double tallest  = double(chrome_h + camera_h - extra_h) / base_h;
            const double fit      = std::min(level, tallest);
            zoom      = zoom_step(fit);
            control_w = std::max(natural, int(std::ceil(zoom * base_w)) + extra_w);
            if (fit < 2)
                feed_h = std::min<double>(camera_h, extra_h + zoom * base_h - chrome_h);
        }
        const int feed_width = std::max(camera_column->CalcMin().x,
                                        std::min(int(std::ceil(feed_h * aspect)), row_width - control_w));
        if (row_width - feed_width > natural)
            target = row_width - feed_width;

        // The camera's minimum width can leave less than the zoom needs.
        if (base_w > 0 && base_h > 0)
            zoom = std::min(zoom, zoom_step(double((target == wxDefaultCoord ? natural : target) - extra_w) / base_w));
    }

    const bool zoom_changed = ams && std::abs(current_zoom - zoom) > 0.001;

    const bool width_changed = std::abs(m_machine_ctrl_panel->GetMinSize().x - target) > 1;
    if (!zoom_changed && !width_changed)
        return;

#if BBL_ENABLE_AMS_CONTROL_WEB && !defined(__WXOSX__)
    if (zoom_changed)
        m_ams_control_web_panel->SetFitZoom(zoom);
#endif
    if (width_changed)
        m_machine_ctrl_panel->SetMinSize(wxSize(target, wxDefaultCoord));
    Layout();
}
