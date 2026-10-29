#ifndef PROBE_OBJECT_H
#define PROBE_OBJECT_H
#include <string>
class wxObject {};
class wxString {
public:
    std::string text;
    wxString(const char* value = "") : text(value) {}
};
const wxString wxEmptyString;
#define WXDLLIMPEXP_BASE
#define WXUNUSED(name)
#endif
