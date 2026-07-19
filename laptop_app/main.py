import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime, timezone
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication,QDialog,QVBoxLayout,QLabel,QCheckBox,QPushButton,QWizard,QWizardPage,QLineEdit,QFormLayout,QSystemTrayIcon,QMenu,QMessageBox
from core.config import load,save,update,CONFIG_DIR
from core.pairing import ensure_laptop_identity
from core.firebase_sync import FirebaseSync
from core.cooldown_manager import CooldownManager
from core.screen_monitor import ScreenMonitor
from core.alarm_engine import AlarmEngine
from ui.components.alarm_overlay import AlarmOverlay
from ui.main_window import MainWindow
ROOT=Path(__file__).parent
LOG_DIR=CONFIG_DIR/'logs'
class Disclaimer(QDialog):
 def __init__(self):
  super().__init__();self.setWindowTitle('Before You Continue');self.setMinimumSize(620,410);l=QVBoxLayout(self);l.addWidget(QLabel('⚠️',styleSheet='font-size:54px;color:#FF8C00;',alignment=Qt.AlignmentFlag.AlignCenter));l.addWidget(QLabel('Before You Continue',styleSheet='font-size:30px;font-weight:800;',alignment=Qt.AlignmentFlag.AlignCenter));l.addWidget(QLabel('This app inspects only a screen rectangle that you explicitly select. It does not use a Discord account token, connect to Discord, send messages, or upload screenshots. OCR and image matching can produce false positives or miss visual changes, so keep the crop narrow and test your trigger before relying on it.'));self.check=QCheckBox('I understand that this is a local visual detector and I will configure it responsibly.');l.addWidget(self.check);b=QPushButton('I Understand — Continue Setup');b.setObjectName('success');b.setEnabled(False);self.check.toggled.connect(b.setEnabled);b.clicked.connect(self.accept);l.addWidget(b);e=QPushButton('Exit');e.clicked.connect(self.reject);l.addWidget(e)
class Setup(QWizard):
 def __init__(self,c):
  super().__init__();self.c=c;self.region=c['screen_monitor']['region'];self.setWindowTitle('Rust Raid Alarm Setup')
  monitor=QWizardPage();monitor.setTitle('Screen monitor');monitor.setSubTitle('Select the exact visible banner/notification area and enter text expected when the alert is present. You can refine OCR/template settings later.')
  form=QFormLayout(monitor);self.trigger=QLineEdit(c['screen_monitor']['trigger_text']);self.trigger.setPlaceholderText('Example: your display name or @username');self.region_label=QLabel(self.describe_region());select=QPushButton('Select screen rectangle');select.clicked.connect(self.pick_region);form.addRow('Trigger phrase',self.trigger);form.addRow('Selected region',self.region_label);form.addRow('',select);self.addPage(monitor)
  firebase=QWizardPage();firebase.setTitle('Firebase (optional)');firebase.setSubTitle('Paste a Realtime Database URL now; service-account credentials can be added later in Settings.');firebase_form=QFormLayout(firebase);self.url=QLineEdit(c['firebase']['database_url']);firebase_form.addRow('Database URL',self.url);self.addPage(firebase)
  ready=QWizardPage();ready.setTitle('Ready');ready.setSubTitle('Finish to launch the dashboard. Run a local monitor test from Settings before relying on alerts.');self.addPage(ready)
 def describe_region(self):return f"x={self.region['x']}, y={self.region['y']}, {self.region['width']}×{self.region['height']}" if self.region.get('width') else 'Not selected'
 def pick_region(self):
  from ui.screens.settings_discord import RegionPicker
  self.picker=RegionPicker();self.picker.selected.connect(self.set_region)
 def set_region(self,region):self.region=region;self.region_label.setText(self.describe_region())
 def accept(self):
  if not self.region.get('width') or not self.region.get('height') or not self.trigger.text().strip():
   QMessageBox.warning(self,'Monitor setup required','Select a screen rectangle and enter a trigger phrase before continuing.');self.setCurrentId(0);return
  self.c['screen_monitor'].update({'enabled':True,'region':self.region,'trigger_text':self.trigger.text().strip()});self.c['firebase']['database_url']=self.url.text().strip();self.c['setup_complete']=True;save(self.c);super().accept()
def main():
 LOG_DIR.mkdir(parents=True,exist_ok=True);logging.basicConfig(level=logging.INFO,handlers=[RotatingFileHandler(LOG_DIR/'app.log',maxBytes=1_000_000,backupCount=3),logging.StreamHandler()])
 app=QApplication([]);app.setQuitOnLastWindowClosed(False);app.setStyleSheet((ROOT/'ui/styles/global.qss').read_text());c=load()
 if not c['disclaimer_accepted']:
  if Disclaimer().exec()!=QDialog.DialogCode.Accepted:return 0
  c['disclaimer_accepted']=True;save(c)
 if not c['setup_complete']:
  if Setup(c).exec()!=QDialog.DialogCode.Accepted:return 0
 c=ensure_laptop_identity(load()); firebase=FirebaseSync(c);firebase.connect();overlay=AlarmOverlay();engine=AlarmEngine(c,overlay);cooldown=CooldownManager(c['cooldown']);monitor=ScreenMonitor(c['screen_monitor']);alarm_active=False; remote_cooldown_until=None
 def persist(section,values):
  nonlocal c
  c=update(section,values)
  if section=='screen_monitor':
   was_running=monitor.isRunning()
   if was_running:monitor.stop()
   monitor.update_settings(c['screen_monitor'])
   if c['screen_monitor']['enabled']:monitor.start()
  if section in ('alarm','cooldown'):
   shared=dict(values)
   if section=='cooldown':
    if 'duration_minutes' in shared:shared['cooldown_duration_minutes']=shared.pop('duration_minutes')
   firebase.write_settings(shared)
 def apply_remote_settings(shared):
  """Merge Android/Firebase settings into local runtime state without writing them back."""
  nonlocal c
  alarm_keys=('device_target','active_preset','screen_flash','volume','tts_enabled')
  cooldown_map={'cooldown_duration_minutes':'duration_minutes','auto_silence_minutes':'auto_silence_minutes','quiet_hours_enabled':'quiet_hours_enabled','quiet_hours_start':'quiet_hours_start','quiet_hours_end':'quiet_hours_end'}
  changed=False
  if 'alert_mode' in shared and c['app'].get('phone_alert_mode')!=shared['alert_mode']:c['app']['phone_alert_mode']=shared['alert_mode'];changed=True
  for remote,local in (('vibration','phone_vibration'),('screen_flash','phone_screen_flash'),('volume_override','phone_volume_override'),('phone_sound_preset','phone_sound_preset')):
   if remote in shared and c['app'].get(local)!=shared[remote]:c['app'][local]=shared[remote];changed=True
  for key in alarm_keys:
   if key in shared and c['alarm'].get(key)!=shared[key]:c['alarm'][key]=shared[key];changed=True
  for remote,local in cooldown_map.items():
   if remote in shared and c['cooldown'].get(local)!=shared[remote]:c['cooldown'][local]=shared[remote];changed=True
  if changed:
   cooldown.settings=c['cooldown'];engine.config=c;save(c);event('Applied synchronized settings from Firebase')
 window=MainWindow(c,persist,firebase)
 def clear_activity():
  nonlocal c
  c['activity']=[];save(c);window.log.set_entries([])
 window.log.clear_requested.connect(clear_activity)
 icons={k:QIcon(str(ROOT/'assets/icons'/v)) for k,v in {'monitoring':'tray_idle.png','raid':'tray_alert.png','cooldown':'tray_cooldown.png','disconnected':'tray_idle.png'}.items()}
 tray=QSystemTrayIcon(icons['monitoring'],app);menu=QMenu();open_action=QAction('Open Dashboard',menu);test_action=QAction('Test Raid',menu);ack_action=QAction('Acknowledge',menu);over_action=QAction('Raid Over',menu);settings_action=QAction('Settings',menu);quit_action=QAction('Quit',menu)
 for a in (open_action,test_action,ack_action,over_action):menu.addAction(a)
 menu.addSeparator();menu.addAction(settings_action);menu.addAction(quit_action);tray.setContextMenu(menu);tray.show()
 def display_state(state,seconds=0):
  window.dashboard.set_state(state,seconds);tray.setIcon(icons.get(state,icons['disconnected']));tray.setToolTip({'monitoring':'Rust Raid Alarm — monitoring screen region','raid':'Rust Raid Alarm — RAID DETECTED','cooldown':'Rust Raid Alarm — cooldown active'}.get(state,'Rust Raid Alarm — monitor stopped'));ack_action.setVisible(state=='raid');over_action.setVisible(state=='cooldown')
 def event(text):
  stamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S');record=f'{stamp}  {text}';c['activity'].append(record);c['activity']=c['activity'][-200:];save(c);window.dashboard.add_event(text);window.log.add_record(record);firebase.log({'timestamp':stamp,'description':text,'type':('raid' if 'Alert detected' in text else 'acknowledged' if 'Acknowledged' in text else 'cooldown' if 'Cooldown' in text else 'error' if 'error' in text.lower() else 'system')})
 def raid(data):
  nonlocal alarm_active
  if cooldown.remaining():
   event('Cooldown blocked screen trigger');return
  if alarm_active:return
  remote=bool(data.get('remote'));triggered_at=data.get('triggered_at') or datetime.utcnow().isoformat()+'Z';target=data.get('target') or c['alarm']['device_target'];preset=c['alarm']['active_preset'];local_mode=data.get('mode') or ('silent' if cooldown.in_quiet_hours() or preset=='stealth' else 'critical');phone_mode='silent' if local_mode=='silent' else c['app'].get('phone_alert_mode','critical')
  # A phone-only remote event must not make the laptop alarm; each device respects the state target.
  if remote and target not in ('laptop','both'):return
  alarm_active=True;engine.trigger(force_stealth=(local_mode=='silent'));cooldown.arm_auto_silence()
  if not remote:
   firebase.write_alarm({'alarm_active':True,'acknowledged':False,'triggered_at':triggered_at,'channel_name':'selected screen region','device_target':target,'alert_mode':phone_mode,'phone_vibration':phone_vibration,'phone_screen_flash':phone_flash,'phone_volume_override':phone_volume_override,'phone_sound_preset':phone_sound_preset,'auto_silence_minutes':auto_silence})
   if target in ('phone','both'): firebase.send_phone_alarm(triggered_at,'Visual alert detected',phone_mode,phone_vibration,phone_flash,auto_silence,phone_volume_override,phone_sound_preset)
  display_state('raid');event(('Remote ' if remote else '')+'alert detected: '+data['author']);tray.showMessage('Rust Raid Alarm','Visual trigger detected',QSystemTrayIcon.MessageIcon.Critical,8000)
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
  if data.get('alarm_active') and not alarm_active: raid({'author':'remote device','remote':True,'target':data.get('device_target','both'),'mode':data.get('alert_mode','critical'),'triggered_at':data.get('triggered_at')})
 def update_phone_health(meta):
  seen=meta.get('phone_last_seen')
  if not seen:
   details=firebase.pairing_details();window.dashboard.set_health(phone='linked; waiting for heartbeat' if details['paired_phone_id'] else 'not paired');return
  try:
   age=(datetime.now(timezone.utc)-datetime.fromisoformat(str(seen).replace('Z','+00:00'))).total_seconds()
   window.dashboard.set_health(phone='connected ✓' if age<180 else f'last seen {int(age//60)}m ago')
  except (ValueError,TypeError): window.dashboard.set_health(phone='timestamp unavailable')
 def update_pairing_health(details):
  window.dashboard.set_health(phone=('linked: '+details.get('phone_name','phone')+'; waiting for heartbeat') if details.get('linked') else 'not paired')
 monitor.detected.connect(lambda data:raid({'author':'screen monitor ('+data['reason']+')'}));monitor.state_changed.connect(lambda state:display_state('monitoring' if state=='monitoring' else 'disconnected'));monitor.error.connect(lambda message:event('Screen monitor error: '+message));cooldown.changed.connect(display_state);cooldown.expired.connect(lambda:(display_state('monitoring'),event('Monitoring resumed')));cooldown.auto_silence.connect(lambda:acknowledge('auto-silence'));firebase.remote_state.connect(sync_remote);firebase.remote_settings.connect(apply_remote_settings);firebase.remote_meta.connect(update_phone_health);firebase.pairing_changed.connect(update_pairing_health);firebase.connected.connect(lambda ok:window.dashboard.set_health(firebase='connected ✓' if ok else 'unavailable'));firebase.remote_acknowledged.connect(lambda source:acknowledge('remote:'+str(source or 'device')));window.dashboard.set_health(firebase='connected ✓' if firebase.db else 'unavailable',phone=('linked; waiting for heartbeat' if c['pairing'].get('paired_phone_id') else 'not paired'))
 window.dashboard.test_requested.connect(lambda:raid({'author':'local test'}));window.alarm_test_requested.connect(lambda preset:(engine.trigger(preset),QTimer.singleShot(8000,engine.stop)));window.dashboard.acknowledge_requested.connect(acknowledge);window.dashboard.raid_over_requested.connect(raid_over);window.dashboard.target_changed.connect(lambda x:persist('alarm',{'device_target':x}));window.dashboard.preset_changed.connect(lambda x:persist('alarm',{'active_preset':x}));open_action.triggered.connect(lambda:(window.showNormal(),window.raise_(),window.activateWindow()));settings_action.triggered.connect(lambda:(window.showNormal(),window.route('settings')));test_action.triggered.connect(lambda:raid({'author':'tray test'}));ack_action.triggered.connect(acknowledge);over_action.triggered.connect(raid_over);quit_action.triggered.connect(lambda:(monitor.stop(),firebase.close(),app.quit()));tray.activated.connect(lambda reason:open_action.trigger() if reason==QSystemTrayIcon.ActivationReason.Trigger else None)
 heartbeat=QTimer();heartbeat.timeout.connect(firebase.heartbeat);heartbeat.start(60_000);firebase.heartbeat()
 def retry_firebase():
  if firebase.is_configured() and not firebase.is_connected(): firebase.connect()
 reconnect_timer=QTimer();reconnect_timer.timeout.connect(retry_firebase);reconnect_timer.start(30_000)
 if c['screen_monitor'].get('enabled'):monitor.start()
 else:display_state('disconnected');event('Screen monitor is not configured. Open Settings → Screen Monitor.')
 if not c['app'].get('start_minimized'):window.show()
 return app.exec()
if __name__=='__main__':raise SystemExit(main())
