import json, platform
from pathlib import Path
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QLabel,QCheckBox,QPushButton,QFileDialog,QMessageBox
from core.config import PATH, load, save, validate, reset
from core.system import set_windows_autostart
class AppSettings(QWidget):
 def __init__(self,config,persist):
  super().__init__();self.config=config;self.persist=persist;l=QVBoxLayout(self);title=QLabel('Application');title.setStyleSheet('font-size:20px;font-weight:800;');l.addWidget(title);self.autostart=QCheckBox('Start with Windows');self.autostart.setChecked(config['app'].get('start_with_windows',False));self.minimized=QCheckBox('Start minimized to system tray');self.minimized.setChecked(config['app'].get('start_minimized',False));self.autostart.toggled.connect(self.set_autostart);self.minimized.toggled.connect(lambda value:self.persist('app',{'start_minimized':value}));l.addWidget(self.autostart);l.addWidget(self.minimized);l.addWidget(QLabel(f'Python: {platform.python_version()}\nOS: {platform.platform()}\nLocal config: {PATH}'));export=QPushButton('Export Config Backup');export.clicked.connect(self.export);import_button=QPushButton('Import Config Backup');import_button.clicked.connect(self.import_config);reset_button=QPushButton('Reset All Settings');reset_button.clicked.connect(self.reset_all);l.addWidget(export);l.addWidget(import_button);l.addWidget(reset_button);self.status=QLabel('Configuration is stored locally. Imports are validated before saving.');self.status.setWordWrap(True);l.addWidget(self.status);l.addStretch()
 def set_autostart(self,value):
  if value and not set_windows_autostart(True):QMessageBox.warning(self,'Autostart unavailable','Windows registry autostart is only available on Windows.');self.autostart.setChecked(False);return
  if not value:set_windows_autostart(False)
  self.persist('app',{'start_with_windows':value})
 def export(self):
  path,_=QFileDialog.getSaveFileName(self,'Export configuration','rust-raid-config.json','JSON (*.json)')
  if path:Path(path).write_text(json.dumps(load(),indent=2,ensure_ascii=False),encoding='utf-8');self.status.setText('Configuration backup exported. Keep it private: it may contain Firebase credentials.')
 def import_config(self):
  path,_=QFileDialog.getOpenFileName(self,'Import configuration','','JSON (*.json)')
  if not path:return
  try:
   candidate=validate(json.loads(Path(path).read_text(encoding='utf-8')));save(candidate);self.status.setText('Validated configuration imported. Restart to apply all service settings.');QMessageBox.information(self,'Imported','Configuration imported successfully. Restart the application to reload every service.')
  except Exception as exc:QMessageBox.warning(self,'Import failed',str(exc))
 def reset_all(self):
  text='Reset local settings, disable autostart, clear activity, and return to first-run setup? Firebase data is not deleted.'
  if QMessageBox.question(self,'Reset settings',text)==QMessageBox.StandardButton.Yes:
   set_windows_autostart(False);reset(keep_disclaimer=True);self.status.setText('Local settings reset. Restart the application to begin setup again.');QMessageBox.information(self,'Reset complete','Local settings were reset. Restart the application to begin setup.')
