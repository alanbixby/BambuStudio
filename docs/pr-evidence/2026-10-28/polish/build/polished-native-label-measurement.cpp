// Hidden regression harness. No wx Show(), event loop, GL, or Studio process.
#include <wx/wx.h>
#include <gtk/gtk.h>
#include <wx/sysopt.h>
#include <fontconfig/fontconfig.h>
#include <cstdio>
#include <cstdlib>

static unsigned invalidations;
extern "C" void __real_gtk_style_context_invalidate(GtkStyleContext*);
extern "C" void __wrap_gtk_style_context_invalidate(GtkStyleContext* context)
{
    ++invalidations;
    __real_gtk_style_context_invalidate(context);
}

class MeasurementApp : public wxApp
{
public:
    bool OnInit() override { return true; }
};
wxIMPLEMENT_APP_NO_MAIN(MeasurementApp);

class PreferredSizeProbe : public wxControl
{
public:
    using wxControl::GTKGetPreferredSize;
};

static bool CheckLabel(wxWindow* parent, int dpi, const char* text, int points,
                       const char* family)
{
    wxStaticText* label = new wxStaticText(parent, wxID_ANY, text);
    GtkWidget* widget = label->GetHandle();
    const wxSize initial = label->GetBestSize(); // Prime the GTK theme-font cache.
    const unsigned beforeFont = invalidations;
    label->SetFont(wxFont(wxFontInfo(points).FaceName(family)));
    const wxSize immediate = label->GetBestSize();
    const unsigned fontInvalidations = invalidations - beforeFont;
    GtkStyleContext* style = gtk_widget_get_style_context(widget);
    PangoFontDescription* expectedFont = NULL;
    gtk_style_context_get(style, gtk_style_context_get_state(style),
                          "font", &expectedFont, NULL);
    const PangoFontDescription* currentFont = pango_context_get_font_description(
        gtk_widget_get_pango_context(widget));
    const bool mismatch = !pango_font_description_equal(expectedFont, currentFont);
    gchar* expectedText = pango_font_description_to_string(expectedFont);
    gchar* currentText = pango_font_description_to_string(currentFont);
    // A fresh Pango layout using the CSS font is independent of GTK's requisition.
    PangoLayout* layout = pango_layout_new(gtk_widget_get_pango_context(widget));
    pango_layout_set_font_description(layout, expectedFont);
    pango_layout_set_text(layout, text, -1);
    int pangoWidth, pangoHeight;
    pango_layout_get_pixel_size(layout, &pangoWidth, &pangoHeight);
    g_object_unref(layout);
    // Explicit synchronization is the oracle, AFTER the immediate read.
    gtk_style_context_invalidate(style);
    gtk_label_set_line_wrap(GTK_LABEL(widget), false);
    int w, h;
    gtk_widget_get_size_request(widget, &w, &h);
    gtk_widget_set_size_request(widget, -1, -1);
    GtkRequisition finalSize;
    gtk_widget_get_preferred_size(widget, NULL, &finalSize);
    gtk_widget_set_size_request(widget, w, h);
    bool pass = !mismatch && immediate.x == finalSize.width + 1 &&
                immediate.y == finalSize.height && finalSize.width == pangoWidth &&
                finalSize.height == pangoHeight;
    // Re-enter the actual native measurement rather than wx's cached best size.
    const unsigned beforeStable = invalidations;
    for (int i = 0; i != 100; ++i)
    {
        label->InvalidateBestSize();
        const wxSize repeated = label->GetBestSize();
        pass = pass && repeated == wxSize(finalSize.width + 1, finalSize.height);
    }
    const unsigned stableInvalidations = invalidations - beforeStable;
    pass = pass && stableInvalidations == 0;
    std::printf("dpi=%d text='%s' initial=%dx%d immediate=%dx%d final=%dx%d pango=%dx%d mismatch=%d syncs=%u stable-syncs=%u css='%s' context='%s' %s\n",
                dpi, text, initial.x, initial.y, immediate.x, immediate.y,
                finalSize.width + 1, finalSize.height, pangoWidth + 1, pangoHeight,
                mismatch, fontInvalidations, stableInvalidations, expectedText,
                currentText, pass ? "PASS" : "FAIL");
    g_free(expectedText);
    g_free(currentText);
    pango_font_description_free(expectedFont);
    delete label;
    return pass;
}

static bool CheckExclusions()
{
    PreferredSizeProbe probe;
    GtkWidget* widgets[] = { gtk_label_new("Wrapped label"), gtk_button_new_with_label("Button") };
    bool pass = true;
    for (unsigned i = 0; i != 2; ++i)
    {
        GtkWidget* widget = widgets[i];
        g_object_ref_sink(widget);
        if (i == 0)
            gtk_label_set_line_wrap(GTK_LABEL(widget), true);
        gtk_widget_set_size_request(widget, 79, 35);
        PangoFontDescription* font = pango_font_description_from_string("Sans 23");
        gtk_widget_override_font(widget, font);
        pango_font_description_free(font);
        const unsigned before = invalidations;
        probe.GTKGetPreferredSize(widget);
        int w, h;
        gtk_widget_get_size_request(widget, &w, &h);
        const bool ok = invalidations == before && !gtk_widget_get_visible(widget) &&
                        w == 79 && h == 35;
        std::printf("excluded=%s hidden=1 request=%dx%d syncs=%u %s\n",
                    i == 0 ? "wrapped-label" : "button", w, h,
                    invalidations - before, ok ? "PASS" : "FAIL");
        pass = pass && ok;
        gtk_widget_destroy(widget);
        g_object_unref(widget);
    }
    return pass;
}

int main(int argc, char** argv)
{
    // Process-local registration; no font installation or persistent config.
    const char* fontPath = "/home/bxb/.local/state/bambu-scaling/build-02.08.04.57/source/resources/fonts/HarmonyOS_Sans_SC_Regular.ttf";
    if (!FcConfigAppFontAddFile(FcConfigGetCurrent(), reinterpret_cast<const FcChar8*>(fontPath)))
        return 2;
    if (!wxEntryStart(argc, argv) || !wxTheApp->CallOnInit())
        return 2;
    const int dpi = argc > 1 ? std::atoi(argv[1]) : 96;
    g_object_set(gtk_settings_get_default(), "gtk-xft-dpi", dpi * 1024, NULL);
    gdk_screen_set_resolution(gdk_screen_get_default(), dpi);
    wxSystemOptions::SetOption("gtk.window.font-dpi-scaling", 1);
    wxFrame* frame = new wxFrame(NULL, wxID_ANY, "Hidden font regression");
    wxPanel* panel = new wxPanel(frame);
    bool pass = CheckLabel(panel, dpi, "Calibration title Wiki", 22, "Sans");
    pass = CheckLabel(panel, dpi, "Wiki", 14, "HarmonyOS Sans SC") && pass;
    pass = CheckLabel(panel, dpi, "Calibration title", 22, "HarmonyOS Sans SC") && pass;
    pass = CheckExclusions() && pass;
    const bool hidden = !frame->IsShown() && !gtk_widget_get_mapped(frame->GetHandle());
    std::printf("frame-hidden=%d %s\n", hidden, pass && hidden ? "PASS" : "FAIL");
    delete frame;
    wxTheApp->OnExit();
    wxEntryCleanup();
    return pass && hidden ? 0 : 1;
}
