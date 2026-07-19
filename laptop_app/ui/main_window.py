from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow,QWidget,QHBoxLayout,QStackedWidget,QTabWidget,QLabel,QMessageBox
from ui.components.sidebar import Sidebar
from ui.screens.dashboard import Dashboard
from ui.screens.settings_discord import DiscordSettings
from ui.screens.settings_alarm import AlarmSettings
from ui.screens.settings_cooldown import CooldownSettings
from ui.screens.settings_integrations import IntegrationsSettings
from ui.screens.activity_log import ActivityLog
from ui.screens.settings_app import AppSettings
class MainWindow(QMainWindow):
 alarm_test_requested=pyqtSignal(str)
 def __init__(self,config,save,firebase):
  super().__init__();self.config=config;self.save=save;self.setWindowTitle('Rust Raid Alarm — Command Center');self.resize(1180,760);root=QWidget();self.setCentralWidget(root);l=QHBoxLayout(root);self.sidebar=Sidebar();l.addWidget(self.sidebar);self.stack=QStackedWidget();l.addWidget(self.stack,1);self.dashboard=Dashboard(config);self.stack.addWidget(self.dashboard);tabs=QTabWidget();tabs.addTab(DiscordSettings(config,save),'Screen Monitor');self.alarm_settings=AlarmSettings(config,save);tabs.addTab(self.alarm_settings,'Alarm');tabs.addTab(CooldownSettings(config,save),'Cooldown');tabs.addTab(IntegrationsSettings(config,save,firebase),'Integrations');tabs.addTab(AppSettings(config,save),'App');self.stack.addWidget(tabs);self.log=ActivityLog(config);self.stack.addWidget(self.log);about=QLabel('<h1>Rust Raid Alarm</h1><p>v1.0.0 • local alert client</p><p>Uses an opt-in local screen-region detector; no Discord credentials are used.</p>');self.stack.addWidget(about);self.sidebar.selected.connect(self.route);self.alarm_settings.test_requested.connect(self.alarm_test_requested)
 def route(self,key): self.stack.setCurrentIndex({'dashboard':0,'settings':1,'log':2,'about':3}[key]); self.log.refresh() if key=='log' else None
