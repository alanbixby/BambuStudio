void StatusBasePanel::fit_camera_to_feed()
{
    if (is_camera_fullscreen() || !m_media_ctrl || !m_machine_ctrl_panel || !m_camera_media_sizer)
        return;

    wxSizer *control_sizer = m_machine_ctrl_panel->GetSizer();
    wxSizer *camera_column = m_camera_media_sizer;
    wxSizerItem *camera_item = camera_column->GetItem(m_media_ctrl);
    if (!control_sizer || !camera_item)
        return;

    const int natural = control_sizer->CalcMin().x;
    // Ignore the old virtual width when the window is narrowed.
    const int row_width = std::max(camera_column->CalcMin().x + natural,
                                   GetClientSize().x - 3 * PAGE_SPACING);
    const int column_h = camera_column->GetSize().y;
    const int camera_h = column_h - camera_column->CalcMin().y + camera_item->GetMinSizeWithBorder().y;
    int target = wxDefaultCoord;
    if (m_media_ctrl->IsShown() && camera_h > 0 && row_width > 0) {
        wxSize video = m_media_ctrl->GetVideoSize();
        if (video.x <= 0 || video.y <= 0)
            video = wxSize(16, 9);
        const double aspect = double(video.x) / video.y;
        const int feed_width = std::max(camera_column->CalcMin().x,
                                        std::min(int(std::ceil(camera_h * aspect)), row_width - natural));
        if (row_width - feed_width > natural)
            target = row_width - feed_width;
    }

    if (std::abs(m_machine_ctrl_panel->GetMinSize().x - target) <= 1)
        return;
    m_machine_ctrl_panel->SetMinSize(wxSize(target, wxDefaultCoord));
    Layout();
    FitInside();
}
