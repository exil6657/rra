import json, platform, shutil
from pathlib import Path
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QLabel,QCheckBox,QPushButton,QFileDialog,QMessageBox
from core.config import PATH, load, save
from core.system import set_windows_autostart
class AppSettings(QWidget):
 def __init__(self,config,persist):
  super().__init__();self.config=config;self.persist=persist;l=QVBoxLayout(self);l.addWidget(QLabel('Application',styleSheet='font-size:20px;font-weight:800;'));self.autostart=QCheckBox('Start with Windows');self.autostart.setChecked(config['app'].get('start_with_windows',False));self.minimized=QCheckBox('Start minimized to system tray');self.minimized.setChecked(config['app'].get('start_minimized',False));self.autostart.toggled.connect(self.set_autostart);self.minimized.toggled.connect(lambda v:self.persist('app',{'start_minimized':v}));l.addWidget(self.autostart);l.addWidget(self.minimized);l.addWidget(QLabel(f'Python: {platform.python_version()}\nOS: {platform.platform()}\nLocal config: {PATH}'));export=QPushButton('Export Config Backup');export.clicked.connect(self.export);import_button=QPushButton('Import Config Backup');import_button.clicked.connect(self.import_config);reset=QPushButton('Reset All Settings');reset.clicked.connect(self.reset);l.addWidget(export);l.addWidget(import_button);l.addWidget(reset);l.addStretch()
 def set_autostart(self,v):
  if v and not set_windows_autostart(True): QMessageBox.warning(self,'Autostart unavailable','Windows registry autostart is only available on Windows.');self.autostart.setChecked(False);return
  if not v:set_windows_autostart(False)
  self.persist('app',{'start_with_windows':v})
 def export(self):
  p,_=QFileDialog.getSaveFileName(self,'Export configuration','rust-raid-config.json','JSON (*.json)')
  if p:Path(p).write_text(json.dumps(load(),indent=2),encoding='utf-8')
 def import_config(self):
  p,_=QFileDialog.getOpenFileName(self,'Import configuration','','JSON (*.json)')
  if not p:return
  try:
   candidate=json.loads(Path(p).read_text(encoding='utf-8'))
   if not isinstance(candidate,dict):raise ValueError('Root is not an object')
   save(candidate);QMessageBox.information(self,'Imported','Settings imported. Restart the app to apply every service setting.')
  except Exception as e:QMessageBox.warning(self,'Import failed',str(e))
 def reset(self):
  if QMessageBox.question(self,'Reset settings','Delete all local settings and restart setup next launch?')==QMessageBox.StandardButton.Yes:
   fresh=load();fresh['setup_complete']=False;fresh['screen_monitor']['enabled']=False;fresh['activity']=[];save(fresh);QMessageBox.information(self,'Reset complete','Settings reset. Restart the application.')
