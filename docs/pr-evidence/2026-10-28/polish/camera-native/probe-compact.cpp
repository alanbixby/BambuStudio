#include <wx/wx.h>
#include <wx/scrolwin.h>
#include <wx/evtloop.h>
#include <wx/sysopt.h>
#include <gtk/gtk.h>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <cstdlib>
#include <sstream>
#include <string>
#define BBL_ENABLE_AMS_CONTROL_WEB 1
#define PAGE_SPACING FromDIP(10)

class FakeMedia : public wxPanel {
public:
 using wxPanel::wxPanel;
 wxSize GetVideoSize() const { return wxSize(0,0); } // Production 16:9 fallback, disconnected.
};
class FakeAMS : public wxPanel {
 double zoom=1;
public:
 explicit FakeAMS(wxWindow* p):wxPanel(p) { SetMinSize(wxSize(GetBaseWidth(),GetBaseHeight())); }
 int GetBaseWidth() const { return FromDIP(586); }
 int GetBaseHeight() const { return FromDIP(340); }
 double GetFitZoom() const { return zoom; }
 void SetFitZoom(double z) { zoom=z; SetMinSize(wxSize(int(std::ceil(z*GetBaseWidth())),int(std::ceil(z*GetBaseHeight())))); }
};
class StatusBasePanel : public wxScrolledWindow {
public:
 FakeMedia* m_media_ctrl=nullptr;
 FakeAMS* m_ams_control_web_panel=nullptr;
 wxPanel *m_machine_ctrl_panel=nullptr,*m_panel_monitoring_title=nullptr,*m_media_play_ctrl=nullptr;
 wxBoxSizer *m_control_rows_sizer=nullptr,*m_camera_media_sizer=nullptr;
 int sizeEvents=0, fitCalls=0;
 bool is_camera_fullscreen() const { return false; }
 void fit_camera_to_feed();
 wxPanel* panel(wxWindow* parent,int w,int h) {
  auto* p=new wxPanel(parent); p->SetMinSize(wxSize(w<0?w:FromDIP(w),h<0?h:FromDIP(h))); return p;
 }
 StatusBasePanel(wxWindow* parent,bool ams):wxScrolledWindow(parent,wxID_ANY,wxDefaultPosition,wxDefaultSize,wxHSCROLL|wxVSCROLL) {
  SetScrollRate(25,25);
  gtk_scrolled_window_set_overlay_scrolling(GTK_SCROLLED_WINDOW(GetHandle()),FALSE);
  auto* outer=new wxBoxSizer(wxVERTICAL);
  outer->Add(panel(this,-1,10),0,wxEXPAND);
  auto* row=new wxBoxSizer(wxHORIZONTAL);
  row->Add(panel(this,10,-1),0,wxEXPAND);
  auto* left=new wxBoxSizer(wxVERTICAL);
  m_camera_media_sizer=new wxBoxSizer(wxVERTICAL);
  m_panel_monitoring_title=panel(this,574,36);
  m_camera_media_sizer->Add(m_panel_monitoring_title,0,wxEXPAND);
  m_media_ctrl=new FakeMedia(this); m_media_ctrl->SetMinSize(FromDIP(wxSize(574,288)));
  m_camera_media_sizer->Add(m_media_ctrl,1,wxEXPAND);
  m_media_play_ctrl=panel(this,-1,40);
  m_camera_media_sizer->Add(m_media_play_ctrl,0,wxEXPAND);
  left->Add(m_camera_media_sizer,1,wxEXPAND);
  // Same monitoring-sizer insertion of separator and progress after the playbar.
  m_camera_media_sizer->Add(panel(this,-1,10),0,wxEXPAND);
  m_camera_media_sizer->Add(panel(this,574,160),0,wxEXPAND);
  row->Add(left,1,wxEXPAND);
  row->Add(panel(this,10,-1),0,wxEXPAND);
  m_machine_ctrl_panel=new wxPanel(this);
  auto* control=new wxBoxSizer(wxVERTICAL);
  control->Add(panel(m_machine_ctrl_panel,614,36),0,wxEXPAND);
  m_control_rows_sizer=new wxBoxSizer(wxVERTICAL);
  m_control_rows_sizer->Add(0,0,0,wxTOP,FromDIP(8));
  m_control_rows_sizer->Add(panel(m_machine_ctrl_panel,586,160),0,wxALIGN_CENTER|wxLEFT|wxRIGHT,FromDIP(8));
  m_control_rows_sizer->Add(0,0,0,wxTOP,FromDIP(6));
  if (!ams) m_control_rows_sizer->Add(panel(m_machine_ctrl_panel,586,200),0,wxALIGN_CENTER|wxLEFT|wxRIGHT,FromDIP(8));
  m_ams_control_web_panel=new FakeAMS(m_machine_ctrl_panel);
  m_ams_control_web_panel->Show(ams);
  m_control_rows_sizer->Add(m_ams_control_web_panel,0,wxALIGN_CENTER|wxLEFT|wxRIGHT,FromDIP(8));
  m_control_rows_sizer->Add(0,0,0,wxTOP,FromDIP(6));
  m_control_rows_sizer->Add(panel(m_machine_ctrl_panel,586,80),0,wxALIGN_CENTER|wxLEFT|wxRIGHT,FromDIP(8));
  m_control_rows_sizer->Add(0,0,0,wxTOP,FromDIP(4));
  control->Add(m_control_rows_sizer,1,wxEXPAND);
  m_machine_ctrl_panel->SetSizer(control); m_machine_ctrl_panel->Layout(); control->Fit(m_machine_ctrl_panel);
  row->Add(m_machine_ctrl_panel,0,wxALL,0);
  row->Add(panel(this,10,-1),0,wxEXPAND);
  outer->Add(row,1,wxEXPAND);
  outer->Add(panel(this,-1,10),0,wxEXPAND);
  SetSizerAndFit(outer); Layout();
  Bind(wxEVT_SIZE,[this](wxSizeEvent& e){ ++sizeEvents; e.Skip(); CallAfter([this]{ ++fitCalls; fit_camera_to_feed(); }); });
 }
};
#if TEST_NEW
#include "fit-new.inc"
#else
#include "fit-old.inc"
#endif
class App:public wxApp { public: bool OnInit() override { return true; } };
wxIMPLEMENT_APP_NO_MAIN(App);
static void Pump(int n=12) {
 for(int i=0;i<n;++i) { wxTheApp->Yield(true); wxTheApp->ProcessPendingEvents(); wxMilliSleep(5); }
}
static std::string geometry(StatusBasePanel* p) {
 std::ostringstream s;
 for(wxSize z:{p->GetClientSize(),p->GetVirtualSize(),p->m_media_ctrl->GetSize(),p->m_machine_ctrl_panel->GetSize(),p->m_machine_ctrl_panel->GetMinSize(),p->m_camera_media_sizer->GetSize()}) s<<z.x<<','<<z.y<<';';
 s<<p->m_ams_control_web_panel->GetFitZoom();return s.str();
}
int main(int argc,char**argv) {
 if(argc!=4 || !std::getenv("CAMERA_PRIVATE_XVFB")) return 90;
 const int dpi=std::atoi(argv[1]); const bool ams=std::string(argv[2])=="web"; const int initialH=std::atoi(argv[3]);
 wxSystemOptions::SetOption("gtk.window.font-dpi-scaling",1);
 if(!wxEntryStart(argc,argv)||!wxTheApp->CallOnInit()) return 91;
 auto* settings=gtk_settings_get_default();auto* screen=gdk_screen_get_default();
 g_object_set(settings,"gtk-xft-dpi",dpi*1024,"gtk-overlay-scrolling",FALSE,"gtk-enable-animations",FALSE,"gtk-theme-name","Adwaita",nullptr);
 gdk_screen_set_resolution(screen,dpi);
 auto* frame=new wxFrame(nullptr,wxID_ANY,"Private disconnected camera sizing probe");
 auto* p=new StatusBasePanel(frame,ams);
 // Frame owns one child without a sizer: permit intentionally undersized clients.
 frame->SetClientSize(p->FromDIP(wxSize(2200,initialH)));frame->Show(); Pump(40);
 std::cerr<<"variant="<<TEST_NEW<<" dpi="<<dpi<<" fromdip96="<<p->FromDIP(96)<<" gdk_scale="<<gtk_widget_get_scale_factor(GTK_WIDGET(p->GetHandle()))<<" display="<<gdk_display_get_name(gdk_screen_get_display(screen))<<" ams="<<ams<<" initial_h="<<initialH<<"\n";
 std::cout<<"phase\trequested_w\trequested_h\tclient_w\tclient_h\tvirtual_w\tvirtual_h\tnatural_w\tcamera_w\tcamera_h\tcamera_min_w\tcontrol_w\tcontrol_min_w\tzoom\tsize_events\tfit_calls\tidle_size_events\tidle_fit_calls\tstable\n";
 auto record=[&](std::string phase,int w,int h){
  frame->SetClientSize(p->FromDIP(wxSize(w,h))); Pump(60);
  auto before=geometry(p);int sizes=p->sizeEvents,fits=p->fitCalls;Pump(40);
  auto client=p->GetClientSize(),virt=p->GetVirtualSize();
  int natural=p->m_camera_media_sizer->CalcMin().x+p->FromDIP(614)+3*p->FromDIP(10);
  std::cout<<phase<<'\t'<<w<<'\t'<<h<<'\t'<<client.x<<'\t'<<client.y<<'\t'<<virt.x<<'\t'<<virt.y<<'\t'<<natural<<'\t'<<p->m_media_ctrl->GetSize().x<<'\t'<<p->m_media_ctrl->GetSize().y<<'\t'<<p->m_camera_media_sizer->CalcMin().x<<'\t'<<p->m_machine_ctrl_panel->GetSize().x<<'\t'<<p->m_machine_ctrl_panel->GetMinSize().x<<'\t'<<p->m_ams_control_web_panel->GetFitZoom()<<'\t'<<p->sizeEvents<<'\t'<<p->fitCalls<<'\t'<<p->sizeEvents-sizes<<'\t'<<p->fitCalls-fits<<'\t'<<(before==geometry(p))<<'\n';
 };
 record("wide",2200,initialH);
 record("narrow",1400,initialH);
 record("too_narrow",1000,initialH);
 record("natural_boundary",1218,initialH);
 record("narrow_again",1400,initialH);
 record("wide_again",2200,initialH);
 record("height_grow",2200,1100);
 record("height_shrink",2200,initialH);
 record("narrow_after_height",1400,initialH);
 // Genuine queued first-frame equivalent, no fit/min/layout forcing by the test.
 p->CallAfter([p]{++p->fitCalls;p->fit_camera_to_feed();});Pump(30);
 record("narrow_after_explicit_trigger",1400,initialH);
 frame->Destroy();Pump();wxTheApp->OnExit();wxEntryCleanup();return 0;
}
