// Native GTK3 DIP regression: actual wx methods, hidden wxFrame, no event loop.
#include <wx/wx.h>
#include <gtk/gtk.h>
#include <wx/sysopt.h>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <climits>

class DIPApp : public wxApp { public: bool OnInit() override { return true; } };
wxIMPLEMENT_APP_NO_MAIN(DIPApp);

static bool optedIn;

static bool SetFontDPI(int dpi)
{
    GdkScreen* screen = gdk_screen_get_default();
    GtkSettings* settings = gtk_settings_get_for_screen(screen);
    g_object_set(settings, "gtk-xft-dpi", dpi * 1024, NULL);
    const double actual = gdk_screen_get_resolution(screen);
    if (std::fabs(actual - dpi) > 0.001)
    {
        std::printf("SETTINGS FAIL requested-font-dpi=%d actual-screen-dpi=%g\n", dpi, actual);
        return false;
    }
    return true;
}

static bool Check(wxFrame* frame, int dpi, int scale, const char* phase)
{
    bool pass = true;
    int failures = 0;
    const int expectedDPI = optedIn ? dpi : 96;
    const double factor = expectedDPI / 96.0;
    const wxWindowBase* windows[] = { frame, NULL };
    for (unsigned wi = 0; wi != 2; ++wi)
    {
        const wxWindowBase* window = windows[wi];
        const wxSize exact = wxWindowBase::FromDIP(wxSize(96, 192), window);
        const wxSize inverse = wxWindowBase::ToDIP(wxSize(dpi, dpi * 2), window);
        if (exact != wxSize(expectedDPI, expectedDPI * 2) || inverse != (optedIn ? wxSize(96, 192) : wxSize(dpi, dpi * 2)))
            ++failures;
        // Zero is a size and -1 is wx's unspecified sentinel in both axes.
        const wxSize sentinels[] = { wxSize(0, -1), wxSize(-1, 0), wxSize(-1, -1) };
        for (const wxSize& s : sentinels)
            if (wxWindowBase::FromDIP(s, window) != s || wxWindowBase::ToDIP(s, window) != s)
                ++failures;
        // Known DIP dimensions and pixel dimensions at the explicitly set DPI.
        // Never infer a global ToDIP conversion from an unrelated GTK text size.
        for (int value : { 8, 17, 37, 96, 127, 255, -8, -37, -127 })
        {
            const int pixels = wxWindowBase::FromDIP(value, window);
            const int dips = wxWindowBase::ToDIP(value, window);
            if (std::fabs(pixels - value * factor) > 0.500001 ||
                std::fabs(dips - value / factor) > 0.500001)
                ++failures;
            const int dipRoundtrip = wxWindowBase::ToDIP(pixels, window);
            const int pixelRoundtrip = wxWindowBase::FromDIP(dips, window);
            // Two nearest-integer conversions: error <= .5 + .5 / s for DIPs,
            // <= .5 + .5 * s for pixels; floor because results are integers.
            const int dipTolerance = static_cast<int>(std::floor(0.5 + 0.5 / factor + 1e-8));
            const int pixelTolerance = static_cast<int>(std::floor(0.5 + 0.5 * factor + 1e-8));
            if (std::abs(dipRoundtrip - value) > dipTolerance ||
                std::abs(pixelRoundtrip - value) > pixelTolerance)
                ++failures;
            const wxPoint point = wxWindowBase::FromDIP(wxPoint(value, value * 2), window);
            if (point.x != pixels || point.y != wxWindowBase::FromDIP(value * 2, window))
                ++failures;
        }
        // Exercise public API integer endpoints and both saturation thresholds.
        const int extremes[] = { INT_MIN, INT_MIN+1, -1431655767, -1431655766,
                                 -1431655765, -2, -1, 0, 1, 2, 1431655763,
                                 1431655764, 1431655765, 1431655766, INT_MAX-1, INT_MAX };
        for (int value : extremes)
        {
            for (int inverse = 0; inverse != 2; ++inverse)
            {
                const double product = inverse ? value / factor : value * factor;
                int expected;
                if (value == -1 || value == 0) expected = value;
                else if (product >= INT_MAX) expected = INT_MAX;
                else if (product <= INT_MIN) expected = INT_MIN;
                else
                {
                    expected = static_cast<int>(std::round(product));
                    if (value > 0 && expected < 1) expected = 1;
                    else if (value < -1 && expected > -2) expected = -2;
                }
                const int actual = inverse ? wxWindowBase::ToDIP(value, window)
                                           : wxWindowBase::FromDIP(value, window);
                const wxSize size = inverse ? wxWindowBase::ToDIP(wxSize(value, -1), window)
                                            : wxWindowBase::FromDIP(wxSize(value, -1), window);
                const wxPoint point = inverse ? wxWindowBase::ToDIP(wxPoint(0, value), window)
                                              : wxWindowBase::FromDIP(wxPoint(0, value), window);
                if (actual != expected || size.x != expected || size.y != -1 || point.x != 0 || point.y != expected)
                {
                    ++failures;
                    std::printf("RANGE FAIL value=%d inverse=%d actual=%d expected=%d\n", value, inverse, actual, expected);
                }
            }
        }
        // Rounding small coordinates must not create zero or the -1 sentinel.
        for (int value : { 1, 2, 3 })
            if (wxWindowBase::FromDIP(value, window) < 1 || wxWindowBase::ToDIP(value, window) < 1 ||
                wxWindowBase::FromDIP(-value - 1, window) >= -1 ||
                wxWindowBase::ToDIP(-value - 1, window) >= -1)
                ++failures;
        std::printf("phase=%s dpi=%d gdk-scale=%d pointer=%s from96=%d expected=%d to%d=%d failures=%d\n",
                    phase, dpi, scale, window ? "window" : "NULL", exact.x, expectedDPI,
                    dpi, inverse.x, failures);
    }
    const wxSize sample(37, 127);
    if (frame->FromDIP(sample) != wxWindowBase::FromDIP(sample, frame) ||
        frame->ToDIP(sample) != wxWindowBase::ToDIP(sample, frame))
        ++failures;
    if (gtk_widget_get_scale_factor(frame->GetHandle()) != scale || frame->IsShown() ||
        gtk_widget_get_mapped(frame->GetHandle()))
        ++failures;
    pass = failures == 0;
    std::printf("phase=%s dpi=%d gdk-scale=%d hidden=1 %s\n", phase, dpi, scale, pass ? "PASS" : "FAIL");
    return pass;
}

int main(int argc, char** argv)
{
    const bool dynamic = argc > 1 && std::strcmp(argv[1], "dynamic") == 0;
    const int firstDPI = dynamic ? 96 : (argc > 1 ? std::atoi(argv[1]) : 96);
    const int scale = argc > 2 ? std::atoi(argv[2]) : 1;
    // Set GTK font DPI before constructing anything which might prime wx's cache.
    if (!wxEntryStart(argc, argv) || !SetFontDPI(firstDPI) || !wxTheApp->CallOnInit())
        return 2;
    const char* mode = argc > 3 ? argv[3] : "unset";
    #if wxUSE_SYSTEM_OPTIONS
    if (std::strcmp(mode, "unset") != 0)
        wxSystemOptions::SetOption("gtk.window.font-dpi-scaling", std::atoi(mode));
    #endif
    optedIn = wxSystemOptions::GetOptionInt("gtk.window.font-dpi-scaling") == 1;
    if (optedIn != (wxUSE_SYSTEM_OPTIONS && std::strcmp(mode, "1") == 0)) return 3;
    std::printf("system-option=%s actual=%d\n", mode, wxSystemOptions::GetOptionInt("gtk.window.font-dpi-scaling"));
    wxFrame* frame = new wxFrame(NULL, wxID_ANY, "Hidden native DIP regression");
    bool pass = Check(frame, firstDPI, scale, dynamic ? "prime" : "fixed");
    if (dynamic)
    {
        for (int dpi : { 120, 144, 192, 96 })
        {
            const bool settingsOK = SetFontDPI(dpi);
            pass = Check(frame, dpi, scale, "same-process-change") && settingsOK && pass;
        }
    }
    delete frame;
    wxTheApp->OnExit();
    wxEntryCleanup();
    return pass ? 0 : 1;
}
