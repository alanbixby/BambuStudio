#include <cstring>
#include <cstdlib>
#include <iostream>
#include "wx/sysopt.h"
static int set_calls = 0;
#if wxUSE_SYSTEM_OPTIONS
void wxSystemOptions::SetOption(const wxString& name, int value) {
    if (name.text != "gtk.window.font-dpi-scaling" || value != 1) std::abort();
    ++set_calls;
}
#endif
class GUI_App {
public:
    bool OnInit();
    bool on_init_inner() { return set_calls == EXPECT_SET_CALLS; }
};
bool GUI_App::OnInit()
{
#if defined(__WXGTK3__) && wxUSE_SYSTEM_OPTIONS
    // Enable font-DPI geometry before startup creates any windows.
    wxSystemOptions::SetOption("gtk.window.font-dpi-scaling", 1);
#endif

    return on_init_inner();
}
int main() {
    GUI_App app;
    if (!app.OnInit()) return 1;
    std::cout << "PASS: startup guard EXPECT_SET_CALLS=" << EXPECT_SET_CALLS
              << ", setter precedes simulated inner startup\n";
}
