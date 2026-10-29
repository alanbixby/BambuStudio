#ifdef __WXGTK3__

// ----------------------------------------------------------------------------
// DPI-independent pixels
// ----------------------------------------------------------------------------

// Point-sized GTK fonts follow the screen font resolution even when the
// integer window scale is unchanged. Match DIP geometry to that resolution.
namespace
{

double wxGTKDIPScale(const wxWindowBase* window)
{
    // Keep legacy applications on identity conversions unless they opt in.
    if ( wxSystemOptions::GetOptionInt("gtk.window.font-dpi-scaling") != 1 )
        return 1;

    GtkWidget* const widget = window ? GTK_WIDGET(window->GetHandle()) : NULL;
    GdkScreen* const screen = widget ? gtk_widget_get_screen(widget)
                                    : gdk_screen_get_default();
    if ( !screen )
        return 1;

    // Creating the screen settings applies Xft.dpi/XSETTINGS to its resolution.
    // Read it each time so settings changes and other screens use their own DPI.
    gtk_settings_get_for_screen(screen);
    const double dpi = gdk_screen_get_resolution(screen);
    return dpi > 0 && wxFinite(dpi) ? dpi / 96 : 1;
}

int wxGTKScaleCoord(int value, double scale)
{
    // -1 means "unspecified" and 0 has no size to scale.
    if ( value == -1 || value == 0 )
        return value;

    const double product = value * scale;
    if ( product >= INT_MAX )
        return INT_MAX;
    if ( product <= INT_MIN )
        return INT_MIN;

    int scaled = wxRound(product);
    if ( value > 0 && scaled < 1 )
        scaled = 1;
    // Keep other negative coordinates from becoming the unspecified sentinel.
    else if ( value < -1 && scaled > -2 )
        scaled = -2;
    return scaled;
}

} // anonymous namespace

/* static */
wxSize
wxWindowBase::FromDIP(const wxSize& sz, const wxWindowBase* w)
{
    const double scale = wxGTKDIPScale(w);
    if ( scale == 1 )
        return sz;
    return wxSize(wxGTKScaleCoord(sz.x, scale), wxGTKScaleCoord(sz.y, scale));
}

/* static */
wxSize
wxWindowBase::ToDIP(const wxSize& sz, const wxWindowBase* w)
{
    const double scale = wxGTKDIPScale(w);
    if ( scale == 1 )
        return sz;
    return wxSize(wxGTKScaleCoord(sz.x, 1 / scale),
                  wxGTKScaleCoord(sz.y, 1 / scale));
}

#endif // __WXGTK3__

int main() { return 0; }
