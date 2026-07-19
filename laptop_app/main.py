import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication,QDialog,QVBoxLayout,QLabel,QCheckBox,QPushButton,QWizard,QWizardPage,QLineEdit,QFormLayout,QSystemTrayIcon,QMenu
from core.config import load,save,update
from core.firebase_sync import FirebaseSync
from core.cooldown_manager import CooldownManager
from core.screen_monitor import ScreenMonitor
from core.alarm_engine import AlarmEngine
from ui.components.alarm_overlay import AlarmOverlay
from ui.main_window import MainWindow
ROOT=Path(__file__).parent
class Disclaimer(QDialog):
 def __init__(self):
  super().__init__();self.setWindowTitle('Before You Continue');self.setMinimumSize(620,410);l=QVBoxLayout(self);l.addWidget(QLabel('⚠️',styleSheet='font-size:54px;color:#FF8C00;',alignment=Qt.AlignmentFlag.AlignCenter));l.addWidget(QLabel('Before You Continue',styleSheet='font-size:30px;font-weight:800;',alignment=Qt.AlignmentFlag.AlignCenter));l.addWidget(QLabel('This app inspects only a screen rectangle that you explicitly select. It does not use a Discord account token, connect to Discord, send messages, or upload screenshots. OCR and image matching can produce false positives or miss visual changes, so keep the crop narrow and test your trigger before relying on it.'));self.check=QCheckBox('I understand that this is a local visual detector and I will configure it responsibly.');l.addWidget(self.check);b=QPushButton('I Understand — Continue Setup');b.setObjectName('success');b.setEnabled(False);self.check.toggled.connect(b.setEnabled);b.clicked.connect(self.accept);l.addWidget(b);e=QPushButton('Exit');e.clicked.connect(self.reject);l.addWidget(e)
class Setup(QWizard):
 def __init__(self,c):
  super().__init__();self.c=c;self.setWindowTitle('Rust Raid Alarm Setup')
  for title,fields in [('Screen monitor', []),('Firebase (optional)', [('Database URL','url')]),('Ready',[])]:
   p=QWizardPage();p.setTitle(title);f=QFormLayout(p)
   if title=='Screen monitor':p.setSubTitle('After setup, choose a local screen rectangle and visual/text trigger in Settings → Screen Monitor.')
   if title=='Firebase (optional)':p.setSubTitle('Paste a Realtime Database URL now; credentials can be added in Settings.')
   for label,name in fields:w=QLineEdit();w.setObjectName(name);f.addRow(label,w)
   self.addPage(p)
 def accept(self):self.c['firebase']['database_url']=self.page(1).findChild(QLineEdit,'url').text().strip();self.c['setup_complete']=True;save(self.c);super().accept()
def main():
 logging.basicConfig(level=logging.INFO,handlers=[RotatingFileHandler(ROOT/'logs/app.log',maxBytes=1_000_000,backupCount=3),logging.StreamHandler()])
 app=QApplication([]);app.setQuitOnLastWindowClosed(False);app.setStyleSheet((ROOT/'ui/styles/global.qss').read_text());c=load()
 if not c['disclaimer_accepted']:
  if Disclaimer().exec()!=QDialog.DialogCode.Accepted:return 0
  c['disclaimer_accepted']=True;save(c)
 if not c['setup_complete']:
  if Setup(c).exec()!=QDialog.DialogCode.Accepted:return 0
 c=load(); firebase=FirebaseSync(c);firebase.connect();overlay=AlarmOverlay();engine=AlarmEngine(c,overlay);cooldown=CooldownManager(c['cooldown']);monitor=ScreenMonitor(c['screen_monitor']);alarm_active=False; remote_cooldown_until=None
 def persist(section,values):
  nonlocal c
  c=update(section,values)
  if section=='screen_monitor':
   was_running=monitor.isRunning();
   if was_running:monitor.stop()
   monitor.update_settings(c['screen_monitor'])
   if c['screen_monitor']['enabled']:monitor.start()
  if section in ('alarm','cooldown'): firebase.write_settings(values)
 window=MainWindow(c,persist,firebase)
 icons={k:QIcon(str(ROOT/'assets/icons'/v)) for k,v in {'monitoring':'tray_idle.png','raid':'tray_alert.png','cooldown':'tray_cooldown.png','disconnected':'tray_idle.png'}.items()}
 tray=QSystemTrayIcon(icons['monitoring'],app);menu=QMenu();open_action=QAction('Open Dashboard',menu);test_action=QAction('Test Raid',menu);ack_action=QAction('Acknowledge',menu);over_action=QAction('Raid Over',menu);settings_action=QAction('Settings',menu);quit_action=QAction('Quit',menu)
 for a in (open_action,test_action,ack_action,over_action):menu.addAction(a)
 menu.addSeparator();menu.addAction(settings_action);menu.addAction(quit_action);tray.setContextMenu(menu);tray.show()
 def display_state(state,seconds=0):
  window.dashboard.set_state(state,seconds);tray.setIcon(icons.get(state,icons['disconnected']));tray.setToolTip({'monitoring':'Rust Raid Alarm — monitoring screen region','raid':'Rust Raid Alarm — RAID DETECTED','cooldown':'Rust Raid Alarm — cooldown active'}.get(state,'Rust Raid Alarm — monitor stopped'));ack_action.setVisible(state=='raid');over_action.setVisible(state=='cooldown')
 def event(text):
  stamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S');record=f'{stamp}  {text}';c['activity'].append(record);c['activity']=c['activity'][-200:];save(c);window.dashboard.add_event(text);firebase.log({'timestamp':stamp,'description':text})
 def raid(data):
  nonlocal alarm_active
  if cooldown.remaining():event('Cooldown blocked screen trigger');return
  if alarm_active:return
  alarm_active=True;engine.trigger(force_stealth=cooldown.in_quiet_hours());cooldown.arm_auto_silence();firebase.write_alarm({'alarm_active':True,'acknowledged':False,'triggered_at':datetime.utcnow().isoformat()+'Z','channel_name':'selected screen region'});display_state('raid');event('Alert detected: '+data['author']);tray.showMessage('Rust Raid Alarm','Visual trigger detected',QSystemTrayIcon.MessageIcon.Critical,8000)
 def acknowledge(source='laptop'):
  nonlocal alarm_active, remote_cooldown_until
  if not alarm_active and not source.startswith('remote') :return
  alarm_active=False;engine.stop();cooldown.disarm_auto_silence()
  if source.startswith('remote') and remote_cooldown_until:
   try: cooldown.start_until(remote_cooldown_until)
   except (ValueError, TypeError): cooldown.start()
  else: cooldown.start()
  expiry=cooldown.until.astimezone().isoformat() if cooldown.until else None
  if not source.startswith('remote'):firebase.acknowledge(source,expiry)
  display_state('cooldown',cooldown.remaining());event('Acknowledged by '+source)
 def raid_over():
  nonlocal alarm_active
  alarm_active=False;engine.stop();cooldown.disarm_auto_silence();cooldown.end();firebase.write_alarm({'alarm_active':False,'acknowledged':False,'cooldown_until':None});display_state('monitoring');event('Cooldown ended manually')
 def sync_remote(data):
  nonlocal remote_cooldown_until
  remote_cooldown_until=data.get('cooldown_until')
  if data.get('alarm_active') and not alarm_active: raid({'author':'remote device'})
 monitor.detected.connect(lambda data:raid({'author':'screen monitor ('+data['reason']+')'}));monitor.state_changed.connect(lambda state:display_state('monitoring' if state=='monitoring' else 'disconnected'));monitor.error.connect(lambda message:event('Screen monitor error: '+message));cooldown.changed.connect(display_state);cooldown.expired.connect(lambda:(display_state('monitoring'),event('Monitoring resumed')));cooldown.auto_silence.connect(lambda:acknowledge('auto-silence'));firebase.remote_state.connect(sync_remote);firebase.remote_acknowledged.connect(lambda source:acknowledge('remote:'+str(source or 'device')))
 window.dashboard.test_requested.connect(lambda:raid({'author':'local test'}));window.dashboard.acknowledge_requested.connect(acknowledge);window.dashboard.raid_over_requested.connect(raid_over);window.dashboard.target_changed.connect(lambda x:persist('alarm',{'device_target':x}));window.dashboard.preset_changed.connect(lambda x:persist('alarm',{'active_preset':x}));open_action.triggered.connect(lambda:(window.showNormal(),window.raise_(),window.activateWindow()));settings_action.triggered.connect(lambda:(window.showNormal(),window.route('settings')));test_action.triggered.connect(lambda:raid({'author':'tray test'}));ack_action.triggered.connect(acknowledge);over_action.triggered.connect(raid_over);quit_action.triggered.connect(lambda:(monitor.stop(),firebase.close(),app.quit()));tray.activated.connect(lambda reason:open_action.trigger() if reason==QSystemTrayIcon.ActivationReason.Trigger else None)
 heartbeat=QTimer();heartbeat.timeout.connect(firebase.heartbeat);heartbeat.start(60_000);firebase.heartbeat()
 if c['screen_monitor'].get('enabled'):monitor.start()
 else:display_state('disconnected');event('Screen monitor is not configured. Open Settings → Screen Monitor.')
 if not c['app'].get('start_minimized'):window.show()
 return app.exec()
if __name__=='__main__':raise SystemExit(main())
