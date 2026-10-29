#include <wx/app.h>
#include <wx/window.h>
#include <gtk/gtk.h>
#include <wx/sysopt.h>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>

class DIPProbeApp final : public wxApp {
public:
    bool OnInit() override { return true; }
};
wxIMPLEMENT_APP_NO_MAIN(DIPProbeApp);

int main(int argc, char** argv) {
    if (!wxEntryStart(argc, argv)) return 10;
    if (!wxTheApp->CallOnInit()) return 11;
    const char* mode = argc > 1 ? argv[1] : "unset";
    if (std::string(mode) != "unset")
        wxSystemOptions::SetOption("gtk.window.font-dpi-scaling", std::atoi(mode));
    const bool optedIn = wxSystemOptions::GetOptionInt("gtk.window.font-dpi-scaling") == 1;
    GdkScreen* screen = gdk_screen_get_default();
    gtk_settings_get_for_screen(screen);
    g_object_set(gtk_settings_get_default(), "gtk-xft-dpi", 144 * 1024, NULL);
    const double dpi = gdk_screen_get_resolution(screen);
    const wxSize scaled = wxWindow::FromDIP(wxSize(100, -1), nullptr);
    const wxSize original = wxWindow::ToDIP(scaled, nullptr);
    const wxSize zero = wxWindow::FromDIP(wxSize(0, -1), nullptr);
    const char* expectation = std::getenv("PROBE_EXPECT_SCALE");
    const double expected_scale = expectation ? std::strtod(expectation, nullptr) : (optedIn ? dpi / 96.0 : 1.0);
    const int expected = static_cast<int>(std::lround(100 * expected_scale));
    const bool pass = scaled == wxSize(expected, -1)
                   && original == wxSize(100, -1)
                   && zero == wxSize(0, -1);
    std::printf("dpi=%.3f expected_scale=%.3f FromDIP(100,-1)=(%d,%d) ToDIP=(%d,%d) zero=(%d,%d) %s\n",
        dpi, expected_scale, scaled.x, scaled.y, original.x, original.y, zero.x, zero.y,
        pass ? "PASS" : "FAIL");
    wxTheApp->OnExit();
    wxEntryCleanup();
    return pass ? 0 : 12;
}
