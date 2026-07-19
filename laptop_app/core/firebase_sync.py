"""Optional Firebase Realtime Database synchronization with safe local failure handling."""
import json, logging
from datetime import datetime, timezone
from PyQt6.QtCore import QObject, pyqtSignal
class FirebaseSync(QObject):
    connected=pyqtSignal(bool); remote_acknowledged=pyqtSignal(str); remote_state=pyqtSignal(dict); remote_settings=pyqtSignal(dict); remote_meta=pyqtSignal(dict); error=pyqtSignal(str)
    def __init__(self, config):
        super().__init__(); self.config=config; self.db=None; self.app=None; self._listener=None; self._settings_listener=None; self._meta_listener=None; self._alarm_state={}; self._settings_state={}; self._meta_state={}; self._last_ack_signature=None
    def connect(self):
        try:
            import firebase_admin
            from firebase_admin import credentials, db
            raw=self.config['firebase'].get('service_account_json',''); url=self.config['firebase'].get('database_url','')
            if not raw or not url: raise ValueError('Firebase is not configured')
            name='rustraid'
            try: app=firebase_admin.get_app(name)
            except ValueError: app=firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)),{'databaseURL':url},name=name)
            self.app=app; self.db=db.reference('/',app=app); self.connected.emit(True); self._start_listener(); self._start_settings_listener(); self._start_meta_listener(); return True
        except Exception as exc:
            logging.getLogger(__name__).warning('Firebase unavailable: %s',exc); self.error.emit(str(exc)); self.connected.emit(False); return False
    def _start_listener(self):
        if not self.db or self._listener: return
        def changed(event):
            try:
                # Firebase streams send an initial root snapshot and later child-level patches.
                # Reconcile patches into a local snapshot before notifying the UI.
                if event.path in ('/', ''):
                    self._alarm_state=dict(event.data or {}) if isinstance(event.data,dict) else {}
                else:
                    target=self._alarm_state; parts=[p for p in event.path.strip('/').split('/') if p]
                    for part in parts[:-1]:
                        target=target.setdefault(part,{})
                    if parts:
                        if event.data is None: target.pop(parts[-1],None)
                        else: target[parts[-1]]=event.data
                state=dict(self._alarm_state); self.remote_state.emit(state)
                if state.get('acknowledged') and state.get('acknowledged_by'):
                    signature=(state.get('acknowledged_by'),state.get('acknowledged_at'),state.get('cooldown_until'))
                    if signature!=self._last_ack_signature:
                        self._last_ack_signature=signature; self.remote_acknowledged.emit(str(state['acknowledged_by']))
                elif not state.get('acknowledged'): self._last_ack_signature=None
            except Exception: logging.getLogger(__name__).exception('Firebase event processing failed')
        try: self._listener=self.db.child('raid_alarm').listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Firebase listener unavailable: %s',exc)
    def _start_settings_listener(self):
        if not self.db or self._settings_listener: return
        def changed(event):
            try:
                if event.path in ('/', ''): self._settings_state=dict(event.data or {}) if isinstance(event.data,dict) else {}
                else:
                    target=self._settings_state; parts=[p for p in event.path.strip('/').split('/') if p]
                    for part in parts[:-1]: target=target.setdefault(part,{})
                    if parts:
                        if event.data is None: target.pop(parts[-1],None)
                        else: target[parts[-1]]=event.data
                self.remote_settings.emit(dict(self._settings_state))
            except Exception: logging.getLogger(__name__).exception('Firebase settings event processing failed')
        try: self._settings_listener=self.db.child('settings').listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Firebase settings listener unavailable: %s',exc)
    def _start_meta_listener(self):
        if not self.db or self._meta_listener: return
        def changed(event):
            try:
                if event.path in ('/', ''): self._meta_state=dict(event.data or {}) if isinstance(event.data,dict) else {}
                else:
                    target=self._meta_state; parts=[p for p in event.path.strip('/').split('/') if p]
                    for part in parts[:-1]: target=target.setdefault(part,{})
                    if parts:
                        if event.data is None: target.pop(parts[-1],None)
                        else: target[parts[-1]]=event.data
                # Never expose the private FCM token through the UI signal.
                visible={k:v for k,v in self._meta_state.items() if k!='phone_fcm_token'}; self.remote_meta.emit(visible)
            except Exception: logging.getLogger(__name__).exception('Firebase metadata event processing failed')
        try: self._meta_listener=self.db.child('app_meta').listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Firebase metadata listener unavailable: %s',exc)
    def close(self):
        for listener_name in ('_listener','_settings_listener','_meta_listener'):
            listener=getattr(self,listener_name)
            if listener:
                try: listener.close()
                except Exception: pass
                setattr(self,listener_name,None)
    def write_alarm(self, values):
        if self.db: self.db.child('raid_alarm').update(values)
    def write_settings(self, values):
        if self.db: self.db.child('settings').update(values)
    def send_phone_alarm(self, triggered_at, message='Visual alert detected', mode='critical'):
        """Send a high-priority data-only FCM alert to the registered phone.
        FCM is needed because a Realtime Database listener alone is not a reliable way to wake a
        phone from deep idle. Failure leaves the Firebase state as the fallback delivery path.
        """
        if not self.db or not self.app: return False
        try:
            from firebase_admin import messaging
            token=self.db.child('app_meta/phone_fcm_token').get()
            if not token: return False
            notice=messaging.Message(data={'event':'raid_alarm','triggered_at':str(triggered_at),'message':str(message),'mode':str(mode)},android=messaging.AndroidConfig(priority='high',ttl=3600),token=token)
            messaging.send(notice,app=self.app); return True
        except Exception as exc:
            logging.getLogger(__name__).warning('FCM delivery unavailable: %s',exc); self.error.emit(str(exc)); return False
    def log(self, entry):
        if self.db: self.db.child('activity_log/entries').push(entry)
    def heartbeat(self, device='laptop'):
        if self.db: self.db.child('app_meta').update({f'{device}_last_seen':datetime.now(timezone.utc).isoformat()})
    def acknowledge(self, source, cooldown_until=None):
        payload={'alarm_active':False,'acknowledged':True,'acknowledged_by':source,'acknowledged_at':datetime.now(timezone.utc).isoformat()}
        if cooldown_until: payload['cooldown_until']=cooldown_until
        self.write_alarm(payload)
