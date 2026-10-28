
#include "nlohmann/json.hpp"
#include <array>
#include <fstream>
#include <sys/stat.h>
#include <algorithm>
#include <cstdint>
#include <filesystem>
#include <functional>
#include <iostream>
#include <map>
#include <memory>
#include <mutex>
#include <queue>
#include <stdexcept>
#include <string>
#include <vector>
using json=nlohmann::json;
namespace disk=std::filesystem;
static int project_removals=0;
namespace fs {
 using disk::path; using disk::directory_iterator; using disk::exists;
 using disk::is_regular_file; using disk::is_directory; using disk::create_directory;
 std::uintmax_t remove_all(const path& p){++project_removals;return disk::remove_all(p);}
}
#define BOOST_LOG_TRIVIAL(level) std::cerr
static bool on_ui=true;
static bool baseline_mode=false;
static std::queue<std::function<void()>> workers,ui_callbacks;
static int requests=0;
static int posted_events=0;
static int connect_limit=0,total_limit=0;
static std::function<void()> http_hook;
static std::string body="{\"id\":123}";
static unsigned status=200;
void require(bool ok,const std::string& msg){if(!ok)throw std::runtime_error(msg);}
void ui_only(){require(on_ui||baseline_mode,"worker accessed UI-owned model/config/panel");}
struct wxString {
 std::string value;
 wxString()=default;wxString(const char* v):value(v){}wxString(std::string v):value(std::move(v)){}
 bool empty()const{return value.empty();}
 std::string ToStdString()const{return value;}
 std::wstring ToStdWstring()const{return std::wstring(value.begin(),value.end());}
 friend wxString operator+(const wxString& a,const wxString& b){return a.value+b.value;}
 static wxString Format(const char* pattern,const std::string& data){std::string s(pattern);s.replace(s.find("%s"),2,data);return s;}
};
struct wxEvtHandler{void CallAfter(std::function<void()> f){ui_callbacks.push(std::move(f));}};
struct wxPanel:wxEvtHandler{};struct wxWebView{};
struct wxCommandEvent{wxCommandEvent()=default;explicit wxCommandEvent(int){};void SetEventObject(void*){}};
static constexpr int EVT_PROJECT_RELOAD=1;
void wxPostEvent(wxPanel*,const wxCommandEvent&){ui_only();++posted_events;}
using wxStructStat=struct stat;
using wxFileOffset=long long;
int wxStat(const wxString& name,wxStructStat* info){return stat(name.value.c_str(),info);}
namespace boost {
 namespace system{using error_code=std::error_code;}
 namespace algorithm {void to_lower(std::string& s){std::transform(s.begin(),s.end(),s.begin(),[](unsigned char c){return std::tolower(c);});}}
 struct format {explicit format(const char*){};template<class T>format& operator%(const T&){return *this;}};
 std::ostream& operator<<(std::ostream& s,const format&){return s;}
 struct thread{template<class F>thread(F f){workers.push(std::move(f));}void detach(){}};}
struct Info{std::string license="L",model_name="Project A",cover_file="",description="Local metadata",origin="original",copyright="[]";};
struct Design{std::string DesignerId="A",Designer="Example";};
struct Profile{std::string ProfileTile="P",ProfileDescription="",ProfileCover="",ProfileUserName="Example";};
static disk::path fixture;
static int creating_getters=0,scan_calls=0;
static std::queue<std::function<void()>> owner_cleanup;
static std::vector<std::string> cleanup_roles;
struct Model;
namespace Slic3r {void remove_backup(Model&,bool);}
struct Model {
 std::shared_ptr<Info> model_info=std::make_shared<Info>();
 std::shared_ptr<Design> design_info=std::make_shared<Design>();
 std::shared_ptr<Profile> profile_info=std::make_shared<Profile>();
 std::string backup_path;
 std::map<int,int> object_backup_id_map;
 int next_object_backup_id=1;
 std::string design_id,stl_design_id,stl_design_country,makerlab_region,makerlab_name,makerlab_id;
 std::string mk_name,mk_version,md_name,md_value,texture_mesh,step_import_path,step_import_tree_nodes;
 std::string m_assembly_tree_data,m_assembly_tree_json_str,m_assembly_steps_tree_data,m_assembly_steps_json_str,m_assembly_model_json_str;
 std::shared_ptr<int> calib_pa_pattern;
 struct Id{int id=1;}; Id id()const{return {};}
 void clear_objects(){} void clear_materials(){}
 ~Model();
 void set_backup_path(const std::string&);
 void load_from(Model&);
 std::string get_backup_path(){
  ui_only();++creating_getters;
  if(backup_path.empty())backup_path=(fixture/"generated").string();
  disk::create_directories(backup_path+"/3D/Objects");
  disk::create_directories(backup_path+"/Metadata");
  return backup_path;
 }
 std::string get_backup_path(const std::string& sub){
  auto path=get_backup_path()+"/"+sub;
  disk::create_directories(path);return path;
 }
 std::string get_auxiliary_file_temp_path();
 std::string get_auxiliary_file_temp_path_if_initialized()const;
};
struct PathSanitizer {template<class T>static T sanitize(const T& t){return t;}};
namespace Slic3r {void remove_backup(Model& m,bool all){
 ui_only();require(all,"expected whole-backup removal");
 const auto path=m.get_backup_path();
 owner_cleanup.push([path]{ui_only();cleanup_roles.push_back("backup-ui");disk::remove_all(path);});
}}
struct Plater{Model* current=nullptr;Model& model(){ui_only();require(current,"missing model");return *current;}};
struct Config{std::string get_country_code(){ui_only();return "US";}};
struct App:wxEvtHandler{
 Plater p;Config conf;Config* app_config=&conf;
 Plater* plater(){ui_only();return &p;}
 std::string get_http_url(const std::string&,const std::string& path){ui_only();return "https://example.org/"+path;}
 std::string url_encode(const std::string& value){ui_only();return value;}
};
static App app;App& wxGetApp(){return app;}
std::string encode_path(const char* value){return value;}
class Http{
 std::function<void(std::string,unsigned)> complete;
 std::function<void(std::string,std::string,unsigned)> error;
 std::function<void(int,bool&)> progress;
 public:
 using Progress=int;
 static Http get(const std::string&){return {};}
 static std::string url_encode(const std::string& value){return value;}
 Http& timeout_connect(int n){connect_limit=n;return *this;}
 Http& timeout_max(int n){total_limit=n;return *this;}
 Http& header(const std::string&,const std::string&){return *this;}
 Http& on_complete(std::function<void(std::string,unsigned)> f){complete=std::move(f);return *this;}
 Http& on_error(std::function<void(std::string,std::string,unsigned)> f){error=std::move(f);return *this;}
 Http& on_progress(std::function<void(int,bool&)> f){progress=std::move(f);return *this;}
 void perform_sync(){
   require(!on_ui,"HTTP blocked UI thread");++requests;if(http_hook)http_hook();
   bool cancel=false;if(progress)progress(0,cancel);if(cancel)return;
   if(status>=400){if(error)error(body,"",status);}else if(complete)complete(body,status);
 }
};
