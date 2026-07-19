"""Optional Firebase Realtime Database synchronization with safe local failure handling."""
import json, logging
from datetime import datetime, timezone
from PyQt6.QtCore import QObject, pyqtSignal
class FirebaseSync(QObject):
    connected=pyqtSignal(bool); remote_acknowledged=pyqtSignal(str); remote_state=pyqtSignal(dict); remote_settings=pyqtSignal(dict); remote_meta=pyqtSignal(dict); pairing_changed=pyqtSignal(dict); error=pyqtSignal(str)
    def __init__(self, config):
        super().__init__(); self.config=config; self.db=None; self.root=None; self.app=None; self._pair_listener=None; self._unlink_listener=None; self._token_listener=None; self._listener=None; self._settings_listener=None; self._meta_listener=None; self._alarm_state={}; self._settings_state={}; self._meta_state={}; self._last_ack_signature=None
    def connect(self):
        try:
            import firebase_admin
            from firebase_admin import credentials, db
            raw=self.config['firebase'].get('service_account_json',''); url=self.config['firebase'].get('database_url','')
            if not raw or not url: raise ValueError('Firebase is not configured')
            name='rustraid'
            try: app=firebase_admin.get_app(name)
            except ValueError: app=firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)),{'databaseURL':url},name=name)
            self.app=app; self.db=db.reference('/',app=app); laptop_id=self.config['pairing']['laptop_id']; self.root=self.db.child('laptops').child(laptop_id); self.connected.emit(True); self._start_listener(); self._start_settings_listener(); self._start_meta_listener(); self._start_pair_listener(); self._start_unlink_listener(); self._start_token_listener(); return True
        except Exception as exc:
            logging.getLogger(__name__).warning('Firebase unavailable: %s',exc); self.error.emit(str(exc)); self.connected.emit(False); return False
    def _start_listener(self):
        if not self.root or self._listener: return
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
        try: self._listener=self.root.child('raid_alarm').listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Firebase listener unavailable: %s',exc)
    def _start_settings_listener(self):
        if not self.root or self._settings_listener: return
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
        try: self._settings_listener=self.root.child('settings').listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Firebase settings listener unavailable: %s',exc)
    def _start_meta_listener(self):
        if not self.root or self._meta_listener: return
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
        try: self._meta_listener=self.root.child('app_meta').listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Firebase metadata listener unavailable: %s',exc)
    def _start_pair_listener(self):
        """Accept only requests carrying this laptop's locally-held high-entropy secret."""
        if not self.db or self._pair_listener: return
        import secrets
        laptop_id=self.config['pairing']['laptop_id']; expected=self.config['pairing']['pair_secret']; requests=self.db.child('pair_requests').child(laptop_id)
        def changed(event):
            try:
                data=event.data if event.path in ('/', '') else {event.path.strip('/'):event.data}
                if not isinstance(data,dict): return
                for request_id,request in data.items():
                    if not isinstance(request,dict): continue
                    secret=str(request.get('pair_secret','')); token=str(request.get('fcm_token','')); name=str(request.get('phone_name','Android phone')); auth_uid=str(request.get('auth_uid',''))
                    requested_at=int(request.get('requested_at',0) or 0)
                    if requested_at and requested_at < int(datetime.now(timezone.utc).timestamp()*1000)-600_000:
                        requests.child(request_id).delete(); continue
                    if secret and token and auth_uid and secrets.compare_digest(secret,expected):
                        existing=self.config['pairing'].get('paired_phone_id','')
                        if existing and existing!=request_id:
                            # One-phone policy: ignore requests until the user explicitly unlinks.
                            continue
                        self.root.child('app_meta').update({'phone_fcm_token':token,'phone_last_seen':datetime.now(timezone.utc).isoformat(),'paired_phone_name':name,'paired_phone_id':request_id,'paired_auth_uid':auth_uid})
                        self.config['pairing'].update({'paired_phone_id':request_id,'paired_phone_name':name})
                        from core.config import save
                        save(self.config); requests.child(request_id).delete(); self.pairing_changed.emit({'linked':True,'phone_id':request_id,'phone_name':name})
            except Exception: logging.getLogger(__name__).exception('Pairing request processing failed')
        try: self._pair_listener=requests.listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Pairing listener unavailable: %s',exc)
    def _start_unlink_listener(self):
        if not self.db or self._unlink_listener: return
        laptop_id=self.config['pairing']['laptop_id']; requests=self.db.child('unlink_requests').child(laptop_id)
        def changed(event):
            try:
                data=event.data if event.path in ('/', '') else {event.path.strip('/'):event.data}
                if not isinstance(data,dict): return
                current=self.config['pairing'].get('paired_phone_id','')
                current_uid=self.root.child('app_meta/paired_auth_uid').get() if self.root else None
                for request_id,request in data.items():
                    if isinstance(request,dict) and request_id==current and request.get('auth_uid')==current_uid:
                        self.unlink_phone(); requests.child(request_id).delete()
            except Exception: logging.getLogger(__name__).exception('Unlink request processing failed')
        try: self._unlink_listener=requests.listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Unlink listener unavailable: %s',exc)
    def _start_token_listener(self):
        if not self.db or self._token_listener: return
        laptop_id=self.config['pairing']['laptop_id']; requests=self.db.child('token_refresh_requests').child(laptop_id)
        def changed(event):
            try:
                data=event.data if event.path in ('/', '') else {event.path.strip('/'):event.data}
                if not isinstance(data,dict): return
                current=self.config['pairing'].get('paired_phone_id',''); current_uid=self.root.child('app_meta/paired_auth_uid').get() if self.root else None
                for request_id,request in data.items():
                    if isinstance(request,dict) and request_id==current and request.get('auth_uid')==current_uid and request.get('fcm_token'):
                        self.root.child('app_meta/phone_fcm_token').set(str(request['fcm_token'])); requests.child(request_id).delete()
            except Exception: logging.getLogger(__name__).exception('FCM token refresh processing failed')
        try: self._token_listener=requests.listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Token refresh listener unavailable: %s',exc)
    def pairing_details(self):
        pairing=self.config['pairing']; return {'laptop_id':pairing['laptop_id'],'pair_secret':pairing['pair_secret'],'paired_phone_id':pairing.get('paired_phone_id',''),'paired_phone_name':pairing.get('paired_phone_name','')}
    def unlink_phone(self):
        if self.root: self.root.child('app_meta').update({'phone_fcm_token':None,'paired_phone_name':None,'paired_phone_id':None,'paired_auth_uid':None})
        self.config['pairing'].update({'paired_phone_id':'','paired_phone_name':''})
        from core.config import save
        save(self.config); self.pairing_changed.emit({'linked':False})
    def close(self):
        for listener_name in ('_listener','_settings_listener','_meta_listener','_pair_listener','_unlink_listener','_token_listener'):
            listener=getattr(self,listener_name)
            if listener:
                try: listener.close()
                except Exception: pass
                setattr(self,listener_name,None)
    def write_alarm(self, values):
        if self.root: self.root.child('raid_alarm').update(values)
    def write_settings(self, values):
        if self.root: self.root.child('settings').update(values)
    def send_phone_alarm(self, triggered_at, message='Visual alert detected', mode='critical', vibration=True, flash=True):
        """Send a high-priority data-only FCM alert to the registered phone.
        FCM is needed because a Realtime Database listener alone is not a reliable way to wake a
        phone from deep idle. Failure leaves the Firebase state as the fallback delivery path.
        """
        if not self.root or not self.app: return False
        try:
            from firebase_admin import messaging
            token=self.root.child('app_meta/phone_fcm_token').get()
            if not token: return False
            notice=messaging.Message(data={'event':'raid_alarm','triggered_at':str(triggered_at),'message':str(message),'mode':str(mode),'vibration':str(bool(vibration)).lower(),'flash':str(bool(flash)).lower(),'laptop_id':self.config['pairing']['laptop_id']},android=messaging.AndroidConfig(priority='high',ttl=3600),token=token)
            messaging.send(notice,app=self.app); return True
        except Exception as exc:
            logging.getLogger(__name__).warning('FCM delivery unavailable: %s',exc); self.error.emit(str(exc)); return False
    def log(self, entry):
        if self.root: self.root.child('activity_log/entries').push(entry)
    def heartbeat(self, device='laptop'):
        if self.root: self.root.child('app_meta').update({f'{device}_last_seen':datetime.now(timezone.utc).isoformat()})
    def acknowledge(self, source, cooldown_until=None):
        payload={'alarm_active':False,'acknowledged':True,'acknowledged_by':source,'acknowledged_at':datetime.now(timezone.utc).isoformat()}
        if cooldown_until: payload['cooldown_until']=cooldown_until
        self.write_alarm(payload)
