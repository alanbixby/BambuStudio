#pragma once

#include <wx/panel.h>

namespace Slic3r {
class MachineObject;
} // namespace Slic3r

namespace Slic3r::GUI {

class DeviceWebHost;

// Thin wxPanel host for the classic AMSControl WebView page.
// Construction is cheap: DeviceWebHost is created with allow_lazy=true, so the
// WebView / bridge / VM are not built until ShowAndLoad() -> NavigateTo().
class wgtAmsControlWebPanel : public wxPanel
{
public:
    explicit wgtAmsControlWebPanel(wxWindow* parent);
    ~wgtAmsControlWebPanel() override = default;

    void ShowAndLoad();
    void HideAndSuspend();
    void UpdateByMachine(Slic3r::MachineObject* obj);

    // Uniform page zoom used to fill extra Control column space. The page
    // keeps its CSS layout; host and content scale together.
    void   SetFitZoom(double zoom);
    double GetFitZoom() const { return m_fit_zoom; }
    // Physical size at zoom 1.
    int    GetBaseWidth() const;
    int    GetBaseHeight() const;

private:
    DeviceWebHost* m_device_web{ nullptr };
    double         m_fit_zoom{ 1.0 };
};

} // namespace Slic3r::GUI
