import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication,QDialog,QVBoxLayout,QLabel,QCheckBox,QPushButton,QWizard,QWizardPage,QLineEdit,QFormLayout
from core.config import load,save,update
from core.firebase_sync import FirebaseSync
from core.cooldown_manager import CooldownManager
from core.self_bot import DiscordMonitor
from core.alarm_engine import AlarmEngine
from ui.components.alarm_overlay import AlarmOverlay
from ui.main_window import MainWindow
ROOT=Path(__file__).parent
class Disclaimer(QDialog):
 def __init__(self):
  super().__init__();self.setWindowTitle('Before You Continue');self.setMinimumSize(620,410);l=QVBoxLayout(self);l.addWidget(QLabel('⚠️',styleSheet='font-size:54px;color:#FF8C00;',alignment=Qt.AlignmentFlag.AlignCenter));l.addWidget(QLabel('Before You Continue',styleSheet='font-size:30px;font-weight:800;',alignment=Qt.AlignmentFlag.AlignCenter));l.addWidget(QLabel('This app monitors Discord through a Discord application bot that you control. Discord user tokens are passwords: do not share, paste, or automate them. Discord self-bots are prohibited by Discord’s Terms. This program never supports user tokens or attempts to make activity look human. Use only channels where the bot has permission to read messages.'));self.check=QCheckBox('I understand. I will use a bot token and keep credentials private.');l.addWidget(self.check);b=QPushButton('I Understand — Continue Setup');b.setObjectName('success');b.setEnabled(False);self.check.toggled.connect(b.setEnabled);b.clicked.connect(self.accept);l.addWidget(b);e=QPushButton('Exit');e.clicked.connect(self.reject);l.addWidget(e)
class Setup(QWizard):
 def __init__(self,c):
  super().__init__();self.c=c;self.setWindowTitle('Rust Raid Alarm Setup');
  for title,fields in [('Discord bot', [('Bot token','token'),('Channel ID','channel')]),('Firebase (optional)', [('Database URL','url')]),('Ready',[])]:
   p=QWizardPage();p.setTitle(title);f=QFormLayout(p)
   if title=='Discord bot':p.setSubTitle('Create a Discord application bot in the Developer Portal; grant it read access to exactly one channel. User tokens are unsupported.')
   if title=='Firebase (optional)':p.setSubTitle('Paste a Realtime Database URL now; credentials can be added in Settings.')
   for label,name in fields: w=QLineEdit();w.setObjectName(name);w.setEchoMode(QLineEdit.EchoMode.Password if name=='token' else QLineEdit.EchoMode.Normal);f.addRow(label,w)
   self.addPage(p)
 def accept(self):
  p=self.page(0);self.c['discord']['bot_token']=p.findChild(QLineEdit,'token').text().strip();self.c['discord']['channel_id']=p.findChild(QLineEdit,'channel').text().strip();self.c['firebase']['database_url']=self.page(1).findChild(QLineEdit,'url').text().strip();self.c['setup_complete']=True;save(self.c);super().accept()
def main():
 logging.basicConfig(level=logging.INFO,handlers=[RotatingFileHandler(ROOT/'logs/app.log',maxBytes=1_000_000,backupCount=3),logging.StreamHandler()]);app=QApplication([]);app.setStyleSheet((ROOT/'ui/styles/global.qss').read_text());c=load()
 if not c['disclaimer_accepted']:
  if Disclaimer().exec()!=QDialog.DialogCode.Accepted:return 0
  c['disclaimer_accepted']=True;save(c)
 if not c['setup_complete']:
  if Setup(c).exec()!=QDialog.DialogCode.Accepted:return 0
 c=load(); firebase=FirebaseSync(c);firebase.connect();overlay=AlarmOverlay();engine=AlarmEngine(c,overlay);cooldown=CooldownManager(c['cooldown']);window=MainWindow(c,lambda sec,vals:update(sec,vals),firebase);monitor=DiscordMonitor(c)
 def event(text):
  c['activity'].append(text);c['activity']=c['activity'][-200:];save(c);window.dashboard.add_event(text)
 def raid(data):
  if cooldown.remaining():event('Cooldown blocked raid ping');return
  engine.trigger(force_stealth=cooldown.in_quiet_hours());cooldown.arm_auto_silence();firebase.write_alarm({'alarm_active':True,'channel_name':data['channel_name']});window.dashboard.set_state('raid');event('Raid detected from '+data['author'])
 def acknowledge(source='laptop'):
  engine.stop();cooldown.disarm_auto_silence();cooldown.start();firebase.acknowledge(source);window.dashboard.set_state('cooldown',cooldown.remaining());event('Acknowledged by '+source)
 monitor.raid_detected.connect(raid);monitor.state_changed.connect(lambda s: window.dashboard.set_state('monitoring' if s=='connected' else 'disconnected'));cooldown.changed.connect(window.dashboard.set_state);cooldown.auto_silence.connect(lambda:acknowledge('auto-silence'));window.dashboard.test_requested.connect(lambda:raid({'author':'local test','channel_name':'test'}));window.dashboard.acknowledge_requested.connect(acknowledge);window.dashboard.raid_over_requested.connect(cooldown.end);window.dashboard.target_changed.connect(lambda x:update('alarm',{'device_target':x}));window.dashboard.preset_changed.connect(lambda x:update('alarm',{'active_preset':x}));window.show();monitor.start();return app.exec()
if __name__=='__main__':raise SystemExit(main())
