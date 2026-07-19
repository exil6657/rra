"""Optional Firebase Realtime Database synchronization with safe local failure handling."""
import json, logging
from datetime import datetime, timezone
from PyQt6.QtCore import QObject, pyqtSignal
class FirebaseSync(QObject):
    connected=pyqtSignal(bool); remote_acknowledged=pyqtSignal(str); remote_state=pyqtSignal(dict); error=pyqtSignal(str)
    def __init__(self, config):
        super().__init__(); self.config=config; self.db=None; self._listener=None; self._alarm_state={}; self._last_ack_signature=None
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
