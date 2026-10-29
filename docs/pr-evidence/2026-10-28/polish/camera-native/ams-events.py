from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'probe-standard.cpp').read_text()
s=s.replace('SetMinSize(wxSize(GetBaseWidth(),GetBaseHeight()));','SetMinSize(wxSize(FromDIP(586),FromDIP(340)));')
s=s.replace('int GetBaseHeight() const { return FromDIP(340); }','int GetBaseHeight() const { return int(std::lround(GetMinSize().y / zoom)); }')
s=s.replace('void SetFitZoom(double z) { zoom=z; SetMinSize(wxSize(int(std::ceil(z*GetBaseWidth())),int(std::ceil(z*GetBaseHeight())))); }','''void SetFitZoom(double z) {
  zoom=z;
  // Fixed synthetic page content report: production host lround(FromDIP * zoom).
  wxSize content_size(int(std::lround(FromDIP(586)*z)),int(std::lround(FromDIP(340)*z)));
  SetMinSize(content_size); SetMaxSize(content_size); SetSize(content_size); Layout();
  // Same native parent/grandparent notification sequence as the production panel callback.
  if (auto* parent=GetParent()) {
   parent->Layout(); parent->SendSizeEvent();
   if (auto* gp=parent->GetParent()) {gp->Layout();gp->SendSizeEvent();}
  }
  // Host's trailing callback notification, now on the stand-in AMS panel.
  Layout(); SendSizeEvent();
 }''')
(R/'probe-ams-events.cpp').write_text(s)
s=(R/'build.py').read_text().replace("str(R/'probe.cpp')","str(R/'probe-ams-events.cpp')").replace("f'probe-{variant}'","f'probe-ams-events-{variant}'").replace("f'compile-{variant}.log'","f'compile-ams-events-{variant}.log'").replace("'compile-commands.json'","'compile-commands-ams-events.json'")
(R/'build-ams-events.py').write_text(s)
s=(R/'run.py').read_text().replace("'run.py'","'run-ams-events.py'").replace("'xvfb.log'","'xvfb-ams-events.log'").replace("'xvfb-command.json'","'xvfb-command-ams-events.json'").replace("['none','web']","['web']").replace('[520,740]','[520]').replace("name=f'{variant}","name=f'ams-events-{variant}").replace("f'probe-{variant}'","f'probe-ams-events-{variant}'").replace("'raw-results.json'","'raw-results-ams-events.json'").replace("'run-commands.json'","'run-commands-ams-events.json'")
(R/'run-ams-events.py').write_text(s)
