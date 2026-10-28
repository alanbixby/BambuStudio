void one_worker(){require(!workers.empty(),"missing worker");auto f=std::move(workers.front());workers.pop();on_ui=false;try{f();}catch(...){on_ui=true;throw;}on_ui=true;}
void one_ui(){require(!ui_callbacks.empty(),"missing UI callback");auto f=std::move(ui_callbacks.front());ui_callbacks.pop();f();}
void drain_ui(){while(!ui_callbacks.empty())one_ui();}
void drain_all(){int count=0;while(!ui_callbacks.empty()||!workers.empty()){require(++count<100,"unbounded scheduler");if(!ui_callbacks.empty())one_ui();else one_worker();}}
void drain_owner(){while(!owner_cleanup.empty()){auto f=std::move(owner_cleanup.front());owner_cleanup.pop();f();}}
void load(ProjectPanel& panel){panel.clear_model_info();wxCommandEvent event;panel.on_reload(event);}
void initialize(Model& model,const char* name){
 model.backup_path=(fixture/name).string();model.design_info->DesignerId=name;model.model_info->model_name=name;
 auto aux=model.get_auxiliary_file_temp_path();disk::create_directories(aux+"/Model Pictures");
 disk::create_directories(aux+"/Others");
 std::ofstream(aux+"/Others/readme.txt")<<"disposable attachment";
 std::ofstream(model.backup_path+"/Metadata/keep.txt")<<"owner cleanup covers siblings";
}
void assert_payload(ProjectPanel& p,const char* name){
 require(!p.m_last_payload.empty(),"missing publication");
 require(p.m_last_payload["model"]["model"]["name"]==name,"stale publication");
 require(p.m_last_payload["model"]["file"]["Other"].size()==1,"real attachment scan failed");
}
void cleanup_test(){
 Model current,incoming;initialize(current,"A");initialize(incoming,"B");app.p.current=&current;
 ProjectPanel panel;panel.m_web_init_completed=true;panel.m_model_id_map={{"A","1"},{"B","2"}};
 load(panel);drain_all();assert_payload(panel,"A");
 const auto old_root=current.backup_path;
 current.load_from(incoming);
 require(incoming.backup_path.empty(),"load_from did not transfer backup ownership");
 require(owner_cleanup.size()==1,"load_from did not retire old backup");
 load(panel);
 require(project_removals==0,"Project performed recursive cleanup on the reload UI path");
 require(disk::exists(old_root+"/Auxiliaries/Others/readme.txt"),"old auxiliary removed before owner cleanup");
 bool heartbeat=false;app.CallAfter([&]{heartbeat=true;});
 drain_all();assert_payload(panel,"B");
 require(heartbeat,"UI heartbeat did not run while owner cleanup was held");
 require(owner_cleanup.size()==1&&disk::exists(old_root+"/Auxiliaries"),"publication required owner cleanup");
 require(scan_calls==2,"expected real Reload worker scans");
 drain_owner();require(!disk::exists(old_root),"owner cleanup lost old backup tree");
 require(disk::exists(current.backup_path+"/Metadata/keep.txt"),"cleanup removed live backup");
 require(cleanup_roles==std::vector<std::string>{"backup-ui"},"unexpected cleanup placement");
 std::cout<<"PASS cleanup: Project makes no deletion; heartbeat and real-file publication precede held owner cleanup; owner removes entire retired tree\n";
}
void identity_test(){
 Model a,empty;initialize(a,"A");app.p.current=&a;
 ProjectPanel panel;panel.m_web_init_completed=true;
 load(panel);one_worker();
 const auto aux=a.get_auxiliary_file_temp_path_if_initialized();
 disk::remove_all(aux);const auto before=creating_getters;
 one_ui(); // clear callback invalidated by generation
 one_ui(); // actual local completion identity check
 require(creating_getters==before&&!disk::exists(aux),"local identity check recreated auxiliary directory");
 require(!panel.m_last_payload.empty(),"unchanged identity rejected local completion");
 disk::remove_all(a.backup_path);
 one_ui(); // actual optional lookup start identity check
 require(creating_getters==before&&!disk::exists(a.backup_path),"lookup-start identity check recreated backup tree");
 one_worker();one_ui(); // actual lookup completion identity check
 require(requests==1&&panel.m_model_id_map.at("A")=="123","optional completion not exercised");
 require(creating_getters==before&&!disk::exists(a.backup_path),"lookup completion recreated backup tree");
 app.p.current=&empty;
 require(!panel.matches_project(aux,"A"),"guard checked only cached panel identity");
 require(creating_getters==before&&!disk::exists(fixture/"generated"),"uninitialized guard allocated backup state");
 const Model& const_empty=empty;
 require(const_empty.get_auxiliary_file_temp_path_if_initialized().empty(),"empty pure accessor changed identity");
 app.p.current=&a;
 a.design_info->DesignerId="changed";
 require(!panel.matches_project(aux,"A"),"changed design identity was accepted");
 a.backup_path="C:\\disposable\\backup";
 require(a.get_auxiliary_file_temp_path_if_initialized()=="C:\\disposable\\backup//Auxiliaries","accessor changed existing separator spelling");
 a.backup_path.clear();
 std::cout<<"PASS identity: all three actual completion/start guards avoid creating getter and filesystem recreation; live Model/design and empty identity checked\n";
}
void reuse_test(){
 Model a,b;initialize(a,"A");initialize(b,"B");
 ProjectPanel panel;panel.m_web_init_completed=true;panel.m_model_id_map={{"A","1"},{"B","2"}};
 const auto before=creating_getters;
 app.p.current=&a;load(panel);
 app.p.current=&b;load(panel);
 app.p.current=&a;load(panel);
 drain_all();assert_payload(panel,"A");
 require(project_removals==0&&owner_cleanup.empty(),"Project queued or performed retired-path deletion on reuse");
 require(disk::exists(a.backup_path+"/Auxiliaries/Others/readme.txt")&&disk::exists(b.backup_path+"/Auxiliaries/Others/readme.txt"),"reload deleted still-owned A/B attachment");
 require(creating_getters==before+3,"completion checks called creating getter on reuse");
 std::cout<<"PASS reuse: rapid A-B-A reloads of still-owned roots preserve files, publish latest A and queue no Project cleanup\n";
}
void lifecycle_test(){
 const auto path=(fixture/"D").string();
 {Model owner;initialize(owner,"D");
  owner.set_backup_path(path);require(owner_cleanup.empty(),"same-path setter retired live backup");
  owner.set_backup_path("detach");require(owner.backup_path.empty()&&owner_cleanup.empty(),"detach lost preservation contract");
 }
 require(disk::exists(path),"detached backup not preserved");
 {Model owner;owner.set_backup_path(path);owner.set_backup_path("");require(owner_cleanup.size()==1,"clearing backup lost cleanup");}
 drain_owner();require(!disk::exists(path),"clear-path cleanup did not remove tree");
 {Model owner;initialize(owner,"E");}
 require(owner_cleanup.size()==1,"destructor lost cleanup");drain_owner();
 require(!disk::exists(fixture/"E"),"destructor tree removal not completed");
 std::cout<<"PASS lifecycle: actual same-path/detach/clear setter and destructor retain cleanup/transfer contracts with modeled backup queue\n";
}
int main(int argc,char** argv){
 try{
  require(argc==3,"usage: binary scratch-fixture-directory cleanup|identity|reuse|lifecycle");
  fixture=argv[1];disk::remove_all(fixture);disk::create_directories(fixture);
  const std::string mode=argv[2];
  if(mode=="cleanup")cleanup_test();else if(mode=="identity")identity_test();
  else if(mode=="reuse")reuse_test();else if(mode=="lifecycle")lifecycle_test();else throw std::runtime_error("unknown test");
  drain_all();drain_owner();disk::remove_all(fixture);return 0;
 }catch(const std::exception& e){std::cerr<<"FAIL: "<<e.what()<<"\n";return 1;}
}
