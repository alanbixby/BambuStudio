
#include <algorithm>
#include <cmath>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
double factor=1;
int FromDIP(int x) { return int(std::lround(x*factor)); }
struct wxSize {
 int x,y;
 wxSize(int a=-1,int b=-1):x(a),y(b){}
 int GetHeight() const {return y;}
 int GetWidth() const {return x;}
 bool operator==(const wxSize& s)const{return x==s.x&&y==s.y;}
 bool operator!=(const wxSize& s)const{return !(*this==s);}
};
const wxSize wxDefaultSize;
struct Window {
 wxSize minimum;
 void SetMinSize(wxSize s){minimum=s;}
 void SetMaxSize(wxSize){}
 void SetSize(wxSize){}
 wxSize GetMinSize()const{return minimum;}
 void Layout(){}
 void SendSizeEvent(){}
 Window* GetParent(){return nullptr;}
};
struct wxWebView {
 bool ready=false;
 float zoom=1.25f;
 int reads=0,writes=0;
 void* GetNativeBackend(){return ready?this:nullptr;}
 float GetZoomFactor(){if(!ready)throw std::runtime_error("read before readiness");++reads;return zoom;}
 void SetZoomFactor(float z){if(!ready)throw std::runtime_error("write before readiness");++writes;zoom=z;}
};
enum class DeviceWebHostMode {DevicePageAmsControlWeb,Other};
constexpr int kAmsControlWebWidthDip=586;
constexpr int kAmsControlWebInitialHeightDip=340;
struct DeviceWebHost:Window {
 DeviceWebHostMode m_mode=DeviceWebHostMode::DevicePageAmsControlWeb;
 wxSize m_last_logical_content_size,m_last_reported_content_size;
 double m_ams_fit_zoom=1,m_ams_base_zoom=-1;
 wxWebView view;
 Window* m_device_webview=nullptr;
 std::function<void(const wxSize&)> m_content_size_changed_handler;
 wxWebView* GetWebView(){return &view;}
 void ApplyAmsControlWebHostSize(int);
 void SetAmsControlWebFitZoom(double);
};
struct wgtAmsControlWebPanel:Window {
 double m_fit_zoom=1;
 DeviceWebHost* m_device_web=nullptr;
 void SetFitZoom(double);
 int GetBaseHeight()const;
 void attach(DeviceWebHost* host);
};
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
void wgtAmsControlWebPanel::attach(DeviceWebHost* host){m_device_web=host;SetMinSize(wxSize(FromDIP(586),FromDIP(340)));host->m_content_size_changed_handler=[this](const wxSize& content_size){
        SetMinSize(content_size);
        SetMaxSize(content_size);
        SetSize(content_size);
        Layout();
        if (auto* parent = GetParent()) {
            parent->Layout();
            parent->SendSizeEvent();
            if (auto* gp = parent->GetParent()) {
                gp->Layout();
                gp->SendSizeEvent();
            }
        }
    };}
void DeviceWebHost::ApplyAmsControlWebHostSize(int height_dip)
{
    constexpr int kMinHeightDip = 220;
    constexpr int kMaxHeightDip = 360;
    height_dip = std::clamp(height_dip, kMinHeightDip, kMaxHeightDip);

    m_last_logical_content_size = wxSize(kAmsControlWebWidthDip, height_dip);
    wxSize content_size(int(std::lround(FromDIP(kAmsControlWebWidthDip) * m_ams_fit_zoom)),
                        int(std::lround(FromDIP(height_dip) * m_ams_fit_zoom)));

#ifndef __WXOSX__
    // wx's macOS zoom is magnification, not layout zoom. StatusPanel keeps
    // the AMS fit at 1 there until a layout-zoom backend is available.
    // Edge creates its native backend asynchronously; a later content-size
    // report retries the pending zoom once the backend exists.
    if (wxWebView* view = GetWebView(); view && view->GetNativeBackend()) {
        if (m_ams_base_zoom <= 0)
            m_ams_base_zoom = view->GetZoomFactor();
        const float zoom = float(m_ams_base_zoom * m_ams_fit_zoom);
        if (std::abs(view->GetZoomFactor() - zoom) > 0.001f)
            view->SetZoomFactor(zoom);
    }
#endif

    if (m_last_reported_content_size != wxDefaultSize) {
        const int jitter = FromDIP(8);
        const int dh = content_size.GetHeight() - m_last_reported_content_size.GetHeight();
        if (dh > -jitter && dh < jitter)
            return;
    }
    if (content_size == m_last_reported_content_size)
        return;

    m_last_reported_content_size = content_size;
    SetMinSize(content_size);
    SetMaxSize(content_size);
    SetSize(content_size);
    if (m_device_webview) {
        m_device_webview->SetMinSize(content_size);
        m_device_webview->SetMaxSize(content_size);
        m_device_webview->SetSize(content_size);
    }
    if (m_content_size_changed_handler)
        m_content_size_changed_handler(content_size);

    Layout();
    if (auto* parent = GetParent()) {
        parent->Layout();
        parent->SendSizeEvent();
    }
}
void DeviceWebHost::SetAmsControlWebFitZoom(double zoom)
{
    if (m_mode != DeviceWebHostMode::DevicePageAmsControlWeb || std::abs(zoom - m_ams_fit_zoom) < 0.001)
        return;

    m_ams_fit_zoom = zoom;
    // Bypass the height jitter filter: the whole size changes.
    m_last_reported_content_size = wxDefaultSize;
    const int height_dip = m_last_logical_content_size.GetHeight() > 0 ?
        m_last_logical_content_size.GetHeight() : kAmsControlWebInitialHeightDip;
    ApplyAmsControlWebHostSize(height_dip);
}
void wgtAmsControlWebPanel::SetFitZoom(double zoom)
{
    m_fit_zoom = zoom;
    if (m_device_web) {
        m_device_web->SetAmsControlWebFitZoom(zoom);
    }
}
int wgtAmsControlWebPanel::GetBaseHeight() const
{
    return int(std::lround(GetMinSize().y / m_fit_zoom));
}
int main(){
 try {
  (void)kAmsControlWebInitialHeightDip;
  int cases=0;
  for(double f:{1.0,1.25,1.5,2.0,2.5}) {
   factor=f;
   for(int height:{220,240,340,360}) {
    DeviceWebHost host;wgtAmsControlWebPanel panel;panel.attach(&host);
#ifdef __WXOSX__
    const int max_step=0;
#else
    const int max_step=20;
#endif
    for(int step=0;step<=max_step;++step) {
     panel.SetFitZoom(1+step/20.0);
     require(panel.GetBaseHeight()==FromDIP(340),"pending zoom changed the unzoomed initial base height");
     require(host.view.reads==0&&host.view.writes==0,"unready backend was queried");
     ++cases;
    }
    host.view.ready=true;
    host.ApplyAmsControlWebHostSize(height);
    require(panel.GetBaseHeight()==FromDIP(height),"first content report did not establish its base height");
#ifndef __WXOSX__
    require(host.view.reads>0,"ready backend did not receive pending zoom");
    require(std::abs(host.view.zoom-1.25*panel.m_fit_zoom)<0.002,"wrong composed pending zoom");
#endif
    for(int step=max_step;step>=0;--step) {
     panel.SetFitZoom(1+step/20.0);
     require(panel.GetBaseHeight()==FromDIP(height),"zoomed reported height failed to round-trip");
     ++cases;
    }
#ifdef __WXOSX__
    require(host.view.reads==0&&host.view.writes==0,"macOS magnification was queried");
#endif
   }
  }
  std::cout<<"PASS: "<<cases<<" extracted-method min-height/zoom checks\n";
  return 0;
 }catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<'\n';return 1;}
}
