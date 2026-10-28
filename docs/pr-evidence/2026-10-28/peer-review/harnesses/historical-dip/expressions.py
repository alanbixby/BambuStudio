"""Original historical extraction patterns and arithmetic assertions."""
import re

FILES = {
    'media': 'src/slic3r/GUI/MediaPlayCtrl.cpp',
    'calib': 'src/slic3r/GUI/calib_dlg.cpp',
    'progress': 'src/slic3r/GUI/Widgets/ProgressDialog.cpp',
    'center': 'src/slic3r/GUI/Widgets/AMSItem.cpp',
    'mapping': 'src/slic3r/GUI/AmsMappingPopup.cpp',
    'sync': 'src/slic3r/GUI/Plater.cpp',
}


def matches(source, regex, count):
    found = re.findall(regex, source)
    assert len(found) == count, (regex, len(found), count)
    return found


def build(inputs, negative_control=False):
    generated = []
    for version in ('before', 'after'):
        sources = {
            key: inputs['before' if negative_control else version][path]
            for key, path in FILES.items()
        }
        media, = matches(sources['media'], r'\bint blank_width\s*=\s*([^;]+);', 1)
        generated.append(f'''
    int media_{version}(int panel_width, int stat_width, int play_width) {{
        Window panel{{{{panel_width, 0}}}}, stat{{{{stat_width, 0}}}}, play{{{{play_width, 0}}}};
        auto GetSize = [&] {{ return panel.GetSize(); }};
        auto* m_label_stat = &stat;
        auto* m_button_play = &play;
        return {media};
    }}
    ''')
        for i, expr in enumerate(matches(sources['calib'], r'\bauto st_size\s*=\s*([^;]+);', 5)):
            generated.append(f'wxSize calib_{version}_{i}(wxSize text_size) {{ return {expr}; }}\n')
        progress = matches(sources['progress'],
                           r'm_msg_scrolledWindow->Set(?:Size|MinSize|MaxSize)\(([^;]*m_msg->GetSize\(\)\.x[^;]*)\);', 3)
        for i, expr in enumerate(progress):
            generated.append(f'''
    wxSize progress_{version}_{i}(int width) {{
        Window msg{{{{width, 0}}}};
        auto* m_msg = &msg;
        return {expr};
    }}
    ''')
        center, = matches(sources['center'], r'\bwxPoint pot\(([^;\n]*tsize\.x[^;\n]*)\);', 1)
        generated.append(f'wxPoint center_{version}(wxSize size, wxSize tsize) {{ return wxPoint({center}); }}\n')
        mapping = matches(sources['mapping'],
                          r'dc.DrawLine\((FromDIP\(1\),\s*(?:FromDIP\(20\)|up),\s*(?:FromDIP\(size.x\)|size.x),\s*(?:FromDIP\(20\)|up))\);', 3)
        for i, args in enumerate(mapping):
            generated.append(f'Line mapping_{version}_{i}(wxSize size, int up) {{ (void)up; return Line{{{args}}}; }}\n')
        sync, = matches(sources['sync'], r'(temp_na_info.dialog_pos\s*=[^;]+;\s*int same_dialog_pos_x[^;]+;\s*temp_na_info.dialog_pos.x[^;]+;\s*temp_na_info.dialog_pos.y[^;]+;)', 1)
        generated.append(f'''
    wxPoint sync_{version}(wxPoint big_btn_pt, wxSize big_btn_size) {{
        struct {{ wxPoint dialog_pos; }} temp_na_info;
        {sync}
        return temp_na_info.dialog_pos;
    }}
    ''')
    
    prelude = r'''
    #include <cmath>
    #include <iostream>
    #include <cstdlib>
    
    struct wxSize {
        int x, y;
        wxSize(int x_, int y_) : x(x_), y(y_) {}
        int GetWidth() const { return x; }
    };
    struct wxPoint {
        int x = 0, y = 0;
        wxPoint() = default;
        wxPoint(int x_, int y_) : x(x_), y(y_) {}
        wxPoint operator+(const wxPoint& p) const { return {x + p.x, y + p.y}; }
    };
    struct Window {
        wxSize size;
        wxSize GetSize() const { return size; }
    };
    struct Line { int x1, y1, x2, y2; };
    double factor = 1;
    int FromDIP(int value) {
        if (value == 0 || value == -1) return value;
        return static_cast<int>(std::lround(value * factor));
    }
    wxSize FromDIP(wxSize value) { return {FromDIP(value.x), FromDIP(value.y)}; }
    int get_sidebar_pos_right_x() { return 1000; }
    int checks = 0;
    void require(bool condition, const char* description) {
        ++checks;
        if (!condition) {
            std::cerr << "FAIL factor=" << factor << ": " << description << '\n';
            std::exit(1);
        }
    }
    '''
    test = r'''
    int main() {
        using Measure = wxSize (*)(wxSize);
        Measure calib_before[] = {calib_before_0, calib_before_1, calib_before_2, calib_before_3, calib_before_4};
        Measure calib_after[] = {calib_after_0, calib_after_1, calib_after_2, calib_after_3, calib_after_4};
        using Progress = wxSize (*)(int);
        Progress progress_before[] = {progress_before_0, progress_before_1, progress_before_2};
        Progress progress_after[] = {progress_after_0, progress_after_1, progress_after_2};
        using Mapping = Line (*)(wxSize, int);
        Mapping mapping_before[] = {mapping_before_0, mapping_before_1, mapping_before_2};
        Mapping mapping_after[] = {mapping_after_0, mapping_after_1, mapping_after_2};
        for (double scale : {0.75, 1.0, 1.25, 1.5, 2.0}) {
            factor = scale;
            int budget = 900 - 150 - 60 - FromDIP(120);
            int actual = media_after(900, 150, 60);
            require(actual == budget, "camera fits remaining pixel budget");
            require(media_after(920, 150, 60) - actual == 20, "20 pane pixels add 20 budget pixels");
            require(media_after(900, 170, 60) - actual == -20, "20 stat pixels consume 20 budget pixels");
            require(media_after(900, 150, 80) - actual == -20, "20 play pixels consume 20 budget pixels");
            require((media_before(900, 150, 60) == actual) == (scale == 1), "original camera counterexample");
    
            int glyph_width = static_cast<int>(72 * scale);
            int padded_width = static_cast<int>(glyph_width * 1.5);
            for (int i = 0; i < 5; ++i) {
                wxSize fixed = calib_after[i]({padded_width, -1});
                wxSize old = calib_before[i]({padded_width, -1});
                require(fixed.x == padded_width && fixed.y == -1, "all five label widths preserve padding and unspecified height");
                require((old.x == fixed.x) == (scale == 1), "all original calibration counterexamples");
            }
            for (int i = 0; i < 3; ++i) {
                wxSize fixed = progress_after[i](240);
                require(fixed.x == 240 + FromDIP(5), "scroll width is measured label plus scaled padding");
                require(fixed.y == FromDIP(150), "nominal scroll height stays scaled once");
                require(progress_after[i](271).x - fixed.x == 31, "31 label pixels add 31 scroll pixels");
                require((progress_before[i](240).x == fixed.x) == (scale == 1), "all original progress width counterexamples");
            }
            for (wxSize size : {wxSize{100, 60}, wxSize{101, 61}, wxSize{10, 5}}) {
                wxPoint fixed = center_after(size, {20, 10});
                require(fixed.x == (size.x - 20) / 2 && fixed.y == (size.y - 10) / 2, "center uses pixel difference including odd/negative results");
            }
            wxPoint centered = center_after({100, 60}, {20, 10});
            wxPoint old_centered = center_before({100, 60}, {20, 10});
            require((old_centered.x == centered.x && old_centered.y == centered.y) == (scale == 1), "original centering counterexample");
            for (int i = 0; i < 3; ++i) {
                Line fixed = mapping_after[i]({137, 60}, 37);
                require(fixed.x1 == FromDIP(1) && fixed.x2 == 137, "line ends at actual pixel width with scaled nominal inset");
                require(fixed.y1 == (i == 1 ? 37 : FromDIP(20)) && fixed.y2 == fixed.y1, "line keeps measured or nominal vertical coordinates");
                require(mapping_after[i]({157, 60}, 37).x2 - fixed.x2 == 20, "20 card pixels add 20 endpoint pixels");
                require((mapping_before[i]({137, 60}, 37).x2 == fixed.x2) == (scale == 1), "all original line endpoint counterexamples");
            }
            wxPoint fixed = sync_after({100, 200}, {90, 30});
            wxPoint old = sync_before({100, 200}, {90, 30});
            require(fixed.x == 1000 + FromDIP(5), "sync x retains sidebar anchor and scaled nominal gap");
            require(fixed.y == 200 + 30 + 3 + FromDIP(2), "sync y uses actual button height and pixel tenth plus scaled gap");
            require(sync_after({100, 200}, {90, 40}).y - fixed.y == 11, "10 button pixels add 11 offset pixels");
            require((old.y == fixed.y) == (scale == 1), "original sync offset counterexample");
            std::cout << "factor=" << scale << " camera " << media_before(900, 150, 60) << " -> " << actual
                      << "; padded label " << calib_before[0]({padded_width, -1}).x << " -> " << padded_width
                      << "; progress " << progress_before[0](240).x << " -> " << progress_after[0](240).x
                      << "; center " << old_centered.x << ',' << old_centered.y << " -> " << centered.x << ',' << centered.y
                      << "; line endpoint " << mapping_before[0]({137, 60}, 37).x2 << " -> 137"
                      << "; sync y " << old.y << " -> " << fixed.y << '\n';
        }
        require(checks == 235, "expected assertion coverage");
        std::cout << checks << " assertions passed\n";
    }
    '''
    return prelude + "".join(generated) + test
