"""Optional Firebase Realtime Database synchronization with safe local failure handling."""
import json, logging
from datetime import datetime, timezone
from PyQt6.QtCore import QObject, pyqtSignal
class FirebaseSync(QObject):
    connected=pyqtSignal(bool); remote_acknowledged=pyqtSignal(str); remote_state=pyqtSignal(dict); error=pyqtSignal(str)
    def __init__(self, config):
        super().__init__(); self.config=config; self.db=None; self._listener=None
    def connect(self):
        try:
            import firebase_admin
            from firebase_admin import credentials, db
            raw=self.config['firebase'].get('service_account_json',''); url=self.config['firebase'].get('database_url','')
            if not raw or not url: raise ValueError('Firebase is not configured')
            name='rustraid'
            try: app=firebase_admin.get_app(name)
            except ValueError: app=firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)),{'databaseURL':url},name=name)
            self.db=db.reference('/',app=app); self.connected.emit(True); self._start_listener(); return True
        except Exception as exc:
            logging.getLogger(__name__).warning('Firebase unavailable: %s',exc); self.error.emit(str(exc)); self.connected.emit(False); return False
    def _start_listener(self):
        if not self.db or self._listener: return
        def changed(event):
            try:
                payload=event.data if isinstance(event.data,dict) else {}
                self.remote_state.emit(payload)
                if payload.get('acknowledged') or payload.get('alarm_active') is False and payload.get('acknowledged_by'):
                    self.remote_acknowledged.emit(str(payload.get('acknowledged_by','remote device')))
            except Exception: logging.getLogger(__name__).exception('Firebase event processing failed')
        try: self._listener=self.db.child('raid_alarm').listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Firebase listener unavailable: %s',exc)
    def close(self):
        if self._listener:
            try: self._listener.close()
            except Exception: pass
            self._listener=None
    def write_alarm(self, values):
        if self.db: self.db.child('raid_alarm').update(values)
    def write_settings(self, values):
        if self.db: self.db.child('settings').update(values)
    def log(self, entry):
        if self.db: self.db.child('activity_log/entries').push(entry)
    def heartbeat(self, device='laptop'):
        if self.db: self.db.child('app_meta').update({f'{device}_last_seen':datetime.now(timezone.utc).isoformat()})
    def acknowledge(self, source, cooldown_until=None):
        payload={'alarm_active':False,'acknowledged':True,'acknowledged_by':source,'acknowledged_at':datetime.now(timezone.utc).isoformat()}
        if cooldown_until: payload['cooldown_until']=cooldown_until
        self.write_alarm(payload)
