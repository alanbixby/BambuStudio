from pathlib import Path
R=Path(__file__).resolve().parent
s=(R/'probe.cpp').read_text()
(R/'probe-standard.cpp').write_text(s)
s=s.replace('panel(m_machine_ctrl_panel,586,200)','panel(m_machine_ctrl_panel,586,160)').replace('panel(m_machine_ctrl_panel,586,220)','panel(m_machine_ctrl_panel,586,200)').replace('panel(m_machine_ctrl_panel,586,100)','panel(m_machine_ctrl_panel,586,80)')
(R/'probe-compact.cpp').write_text(s)
s=(R/'build.py').read_text().replace("str(R/'probe.cpp')","str(R/'probe-compact.cpp')").replace("f'probe-{variant}'","f'probe-compact-{variant}'").replace("f'compile-{variant}.log'","f'compile-compact-{variant}.log'").replace("'compile-commands.json'","'compile-commands-compact.json'")
(R/'build-compact.py').write_text(s)
s=(R/'run.py').read_text().replace("'run.py'","'run-compact.py'").replace("'xvfb.log'","'xvfb-compact.log'").replace("'xvfb-command.json'","'xvfb-command-compact.json'").replace("['none','web']","['none']").replace('[520,740]','[520]').replace("name=f'{variant}","name=f'compact-{variant}").replace("f'probe-{variant}'","f'probe-compact-{variant}'").replace("'raw-results.json'","'raw-results-compact.json'").replace("'run-commands.json'","'run-commands-compact.json'")
(R/'run-compact.py').write_text(s)
