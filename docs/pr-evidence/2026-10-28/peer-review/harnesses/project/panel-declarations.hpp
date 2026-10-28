
public:
 std::vector<std::string> scripts;bool editing=false;
 ~ProjectPanel();
 void on_reload(wxCommandEvent&);
 void clear_model_info();
 void update_model_data();
 std::string get_model_id(std::string);
 bool is_editing_page()const{ui_only();return editing;}
 void RunScript(std::string s){ui_only();scripts.push_back(std::move(s));}
 static std::map<std::string,std::vector<json>> Reload(wxString);
 static std::string formatBytes(unsigned long n){return std::to_string(n);}
 static wxString to_base64(std::string){throw std::runtime_error("image fixtures unsupported");}
 void request_info();
};
