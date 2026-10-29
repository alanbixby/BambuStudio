// Focused C++98 checks. GTK functions and wx value objects are test doubles.
// The conversion bodies, wrappers, rounding helper and sysopt header are extracted.
#include <climits>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>

static unsigned long checks = 0;
static void check(bool ok, const char* message)
{
    ++checks;
    if (!ok) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}

static int option_value = 0;
static unsigned option_reads = 0;
static unsigned state_reads = 0;
static unsigned settings_reads = 0;
static bool forbid_state = false;

#include "wx/sysopt.h"
#if wxUSE_SYSTEM_OPTIONS
int wxSystemOptions::GetOptionInt(const wxString& name)
{
    check(name.text == "gtk.window.font-dpi-scaling", "exact option name");
    ++option_reads;
    return option_value;
}
#endif

struct GdkScreen { double dpi; };
struct GtkWidget { GdkScreen* screen; };
static GdkScreen* default_screen = NULL;

static void read_state()
{
    check(!forbid_state, "window/GDK state accessed while option was off");
    ++state_reads;
}

#define GTK_WIDGET(pointer) static_cast<GtkWidget*>(pointer)
static GdkScreen* gtk_widget_get_screen(GtkWidget* widget)
{
    read_state();
    return widget->screen;
}
static GdkScreen* gdk_screen_get_default()
{
    read_state();
    return default_screen;
}
static void gtk_settings_get_for_screen(GdkScreen*)
{
    read_state();
    ++settings_reads;
}
static double gdk_screen_get_resolution(GdkScreen* screen)
{
    read_state();
    return screen->dpi;
}

struct wxSize
{
    int x, y;
    wxSize(int a, int b) : x(a), y(b) {}
};
struct wxPoint
{
    int x, y;
    wxPoint(int a, int b) : x(a), y(b) {}
};
#define wxASSERT_MSG(condition, message) check(condition, message)
#define wxCHECK_VISUALC_VERSION(version) 0
// Match the GNU C++98 wxFinite branch in the frozen include/wx/math.h.
#define wxFinite(value) finite(value)
@ROUND@

namespace Baseline {
class wxWindowBase
{
    GtkWidget* widget;
public:
    wxWindowBase(GtkWidget* value) : widget(value) {}
    void* GetHandle() const { read_state(); return widget; }
@WRAPPERS@
};
@BASELINE@
}
namespace Candidate {
class wxWindowBase
{
    GtkWidget* widget;
public:
    wxWindowBase(GtkWidget* value) : widget(value) {}
    void* GetHandle() const { read_state(); return widget; }
@WRAPPERS@
};
@CANDIDATE@
}

static void same(wxSize actual, wxSize expected)
{
    check(actual.x == expected.x && actual.y == expected.y, "size conversion mismatch");
}
static void same(wxPoint actual, wxPoint expected)
{
    check(actual.x == expected.x && actual.y == expected.y, "point conversion mismatch");
}

static void identity(int x, int y, const Candidate::wxWindowBase* window)
{
    const wxSize sz(x, y);
    const wxPoint pt(x, y);
    same(Candidate::wxWindowBase::FromDIP(sz, window), sz);
    same(Candidate::wxWindowBase::ToDIP(sz, window), sz);
    same(Candidate::wxWindowBase::FromDIP(pt, window), pt);
    same(Candidate::wxWindowBase::ToDIP(pt, window), pt);
    check(Candidate::wxWindowBase::FromDIP(x, window) == x, "scalar FromDIP identity");
    check(Candidate::wxWindowBase::ToDIP(x, window) == x, "scalar ToDIP identity");
    if (window) {
        same(window->FromDIP(sz), sz);
        same(window->ToDIP(sz), sz);
        same(window->FromDIP(pt), pt);
        same(window->ToDIP(pt), pt);
        check(window->FromDIP(x) == x, "member scalar FromDIP identity");
        check(window->ToDIP(x) == x, "member scalar ToDIP identity");
    }
}

static void preserved(int x, int y, const Baseline::wxWindowBase* old_window,
                      const Candidate::wxWindowBase* new_window)
{
    const wxSize sz(x, y);
    const wxPoint pt(x, y);
    same(Candidate::wxWindowBase::FromDIP(sz, new_window),
         Baseline::wxWindowBase::FromDIP(sz, old_window));
    same(Candidate::wxWindowBase::ToDIP(sz, new_window),
         Baseline::wxWindowBase::ToDIP(sz, old_window));
    same(Candidate::wxWindowBase::FromDIP(pt, new_window),
         Baseline::wxWindowBase::FromDIP(pt, old_window));
    same(Candidate::wxWindowBase::ToDIP(pt, new_window),
         Baseline::wxWindowBase::ToDIP(pt, old_window));
    check(Candidate::wxWindowBase::FromDIP(x, new_window) ==
          Baseline::wxWindowBase::FromDIP(x, old_window), "scalar FromDIP preserved");
    check(Candidate::wxWindowBase::ToDIP(x, new_window) ==
          Baseline::wxWindowBase::ToDIP(x, old_window), "scalar ToDIP preserved");
}

int main(int argc, char** argv)
{
    GdkScreen screen = {144};
    GdkScreen alternate = {192};
    GtkWidget widget = {&screen};
    Baseline::wxWindowBase before(&widget);
    Candidate::wxWindowBase after(&widget);
    Candidate::wxWindowBase no_handle(NULL);
    default_screen = &alternate;
    if (argc == 2 && std::strcmp(argv[1], "--red-control") == 0) {
        forbid_state = true;
        Baseline::wxWindowBase::FromDIP(wxSize(10, -2), &before);
        check(false, "red control unexpectedly passed");
    }

    // Unset/zero/non-1 values, all wrappers, signed extrema and sentinels.
    const int off_values[] = {0, -1, 2, INT_MIN, INT_MAX};
    const int edges[] = {INT_MIN, INT_MIN + 1, -1000000, -3, -2, -1,
                         0, 1, 2, 3, 1000000, INT_MAX - 1, INT_MAX};
    forbid_state = true;
    for (unsigned mode = 0; mode < sizeof(off_values)/sizeof(off_values[0]); ++mode) {
        option_value = off_values[mode];
        for (unsigned i = 0; i < sizeof(edges)/sizeof(edges[0]); ++i) {
            for (unsigned j = 0; j < sizeof(edges)/sizeof(edges[0]); ++j) {
                identity(edges[i], edges[j], &after);
                identity(edges[i], edges[j], &no_handle);
                identity(edges[i], edges[j], NULL);
            }
        }
        for (int i = -2048; i <= 2048; ++i)
            identity(i, -i, &after);
    }
    check(state_reads == 0 && settings_reads == 0, "off path must not touch GTK/window state");
    std::cout << "PASS: off identity, sentinels, signed edges; state reads=0\n";

    option_value = 1;
#if wxUSE_SYSTEM_OPTIONS
    forbid_state = false;
    const double dpis[] = {48, 72, 96, 120, 144, 192, 288, 0, -1,
        std::numeric_limits<double>::quiet_NaN(),
        std::numeric_limits<double>::infinity(),
        std::numeric_limits<double>::max(), std::numeric_limits<double>::min()};
    for (unsigned d = 0; d < sizeof(dpis)/sizeof(dpis[0]); ++d) {
        screen.dpi = dpis[d];
        alternate.dpi = dpis[d];
        for (unsigned i = 0; i < sizeof(edges)/sizeof(edges[0]); ++i)
            for (unsigned j = 0; j < sizeof(edges)/sizeof(edges[0]); ++j) {
                preserved(edges[i], edges[j], &before, &after);
                preserved(edges[i], edges[j], NULL, NULL);
            }
        for (int i = -2048; i <= 2048; ++i)
            preserved(i, -i, &before, &after);
    }
    screen.dpi = 144;
    same(after.FromDIP(wxSize(10, -2)), wxSize(15, -3));
    same(after.ToDIP(wxSize(15, -3)), wxSize(10, -2));
    same(after.FromDIP(wxSize(-1, 0)), wxSize(-1, 0));
    same(after.FromDIP(wxSize(INT_MAX, INT_MIN)), wxSize(INT_MAX, INT_MIN));
    screen.dpi = 192;
    same(after.FromDIP(wxSize(10, -2)), wxSize(20, -4));
    alternate.dpi = 120;
    same(no_handle.FromDIP(wxSize(8, -8)), wxSize(10, -10));
    same(Candidate::wxWindowBase::FromDIP(wxSize(8, -8), NULL), wxSize(10, -10));
    widget.screen = &alternate;
    same(after.FromDIP(wxSize(8, -8)), wxSize(10, -10));
    widget.screen = NULL;
    same(after.FromDIP(wxSize(INT_MAX, -1)), wxSize(INT_MAX, -1));
    default_screen = NULL;
    identity(INT_MIN, INT_MAX, NULL);
    check(settings_reads != 0 && option_reads != 0, "enabled path exercises settings and option");
    option_value = 0;
    const unsigned previous_reads = state_reads;
    forbid_state = true;
    identity(INT_MIN, INT_MAX, &after);
    check(state_reads == previous_reads, "disabling is immediate, no cached scale");
    std::cout << "PASS: enabled equals frozen baseline; DPI changes/screens/fallback/saturation\n";
#else
    identity(INT_MIN, INT_MAX, &after);
    check(state_reads == 0 && option_reads == 0, "actual disabled-options stub stays off");
    std::cout << "PASS: actual wx sysopt disabled stub returns zero; no state reads\n";
    // Keep the baseline comparison helper referenced in the disabled variant.
    (void)&preserved;
#endif
    std::cout << "PASS: " << checks << " checks, wxUSE_SYSTEM_OPTIONS="
              << wxUSE_SYSTEM_OPTIONS << ", C++98\n";
}
