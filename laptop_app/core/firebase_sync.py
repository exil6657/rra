"""Optional Firebase Realtime Database transport. All calls fail closed when not configured."""
import json, logging
from datetime import datetime, timezone
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
class FirebaseSync(QObject):
    connected=pyqtSignal(bool); remote_acknowledged=pyqtSignal(str); remote_state=pyqtSignal(dict)
    def __init__(self, config): super().__init__(); self.config=config; self.db=None
    def connect(self):
        try:
            import firebase_admin
            from firebase_admin import credentials, db
            raw=self.config['firebase'].get('service_account_json',''); url=self.config['firebase'].get('database_url','')
            if not raw or not url: raise ValueError('Firebase is not configured')
            cred=credentials.Certificate(json.loads(raw)); app=firebase_admin.initialize_app(cred,{'databaseURL':url},name='rustraid') if not firebase_admin._apps else firebase_admin.get_app('rustraid')
            self.db=db.reference('/',app=app); self.connected.emit(True); return True
        except Exception as exc: logging.getLogger(__name__).warning('Firebase unavailable: %s',exc); self.connected.emit(False); return False
    def write_alarm(self, values):
        if self.db: self.db.child('raid_alarm').update(values)
    def write_settings(self, values):
        if self.db: self.db.child('settings').update(values)
    def log(self, entry):
        if self.db: self.db.child('activity_log/entries').push(entry)
    def heartbeat(self, device='laptop'):
        if self.db: self.db.child('app_meta').update({f'{device}_last_seen':datetime.now(timezone.utc).isoformat()})
    def acknowledge(self, source): self.write_alarm({'alarm_active':False,'acknowledged':True,'acknowledged_by':source,'acknowledged_at':datetime.now(timezone.utc).isoformat()})
