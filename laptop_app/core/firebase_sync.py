"""Optional Firebase Realtime Database synchronization with safe local failure handling."""
import json, logging
from datetime import datetime, timezone
from PyQt6.QtCore import QObject, pyqtSignal
class FirebaseSync(QObject):
    connected=pyqtSignal(bool); remote_acknowledged=pyqtSignal(str); remote_state=pyqtSignal(dict); remote_settings=pyqtSignal(dict); remote_meta=pyqtSignal(dict); remote_phones=pyqtSignal(dict); pairing_changed=pyqtSignal(dict); error=pyqtSignal(str)
    def __init__(self, config):
        super().__init__(); self.config=config; self.db=None; self.root=None; self.app=None; self._pair_listener=None; self._unlink_listener=None; self._token_listener=None; self._listener=None; self._settings_listener=None; self._meta_listener=None; self._phones_listener=None; self._alarm_state={}; self._settings_state={}; self._meta_state={}; self._last_ack_signature=None; self._connection_fingerprint=None
    def is_configured(self):
        return bool(self.config.get('firebase',{}).get('service_account_json') and self.config.get('firebase',{}).get('database_url'))
    def is_connected(self):
        return self.root is not None
    def _mark_unavailable(self, exc):
        logging.getLogger(__name__).warning('Firebase operation unavailable: %s',exc)
        self.close(); self.root=None; self.db=None
        self.error.emit(str(exc)); self.connected.emit(False)
    def connect(self):
        try:
            import firebase_admin
            from firebase_admin import credentials, db
            raw=self.config['firebase'].get('service_account_json',''); url=self.config['firebase'].get('database_url','')
            if not raw or not url: raise ValueError('Firebase is not configured')
            fingerprint=(raw,url); name='rustraid'
            if self.app and self._connection_fingerprint != fingerprint:
                self.close(); firebase_admin.delete_app(self.app); self.app=None
            try: app=firebase_admin.get_app(name)
            except ValueError: app=firebase_admin.initialize_app(credentials.Certificate(json.loads(raw)),{'databaseURL':url},name=name)
            self.app=app; self._connection_fingerprint=fingerprint; self.db=db.reference('/',app=app); laptop_id=self.config['pairing']['laptop_id']; self.root=self.db.child('laptops').child(laptop_id); self.connected.emit(True); self._start_listener(); self._start_settings_listener(); self._start_meta_listener(); self._start_phones_listener(); self._start_pair_listener(); self._start_unlink_listener(); self._start_token_listener(); return True
        except Exception as exc:
            self.root=None; self.db=None; self._mark_unavailable(exc); return False
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
                elif not state.get('acknowledged'): self._last_ack_signature=None; self._connection_fingerprint=None
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
    def _default_phone_profile(self):
        app=self.config['app']; cooldown=self.config['cooldown']
        return {'alert_mode':app.get('phone_alert_mode','critical'),'vibration':app.get('phone_vibration',True),'screen_flash':app.get('phone_screen_flash',True),'volume_override':app.get('phone_volume_override',True),'sound_preset':app.get('phone_sound_preset','defcon1'),'auto_silence_minutes':cooldown['auto_silence_minutes'],'quiet_hours_enabled':cooldown['quiet_hours_enabled'],'quiet_hours_start':cooldown['quiet_hours_start'],'quiet_hours_end':cooldown['quiet_hours_end']}
    def _start_phones_listener(self):
        if not self.root or self._phones_listener: return
        def changed(event):
            try:
                data=event.data if isinstance(event.data,dict) else {}
                visible={phone_id:{'name':phone.get('identity',{}).get('name','Phone'),'enabled':phone.get('identity',{}).get('enabled',True),'heartbeat':phone.get('heartbeat')} for phone_id,phone in data.items() if isinstance(phone,dict)}
                self.remote_phones.emit(visible)
            except Exception: logging.getLogger(__name__).exception('Phone roster event processing failed')
        try: self._phones_listener=self.root.child('phones').listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Phone roster listener unavailable: %s',exc)
    def _start_pair_listener(self):
        if not self.db or self._pair_listener: return
        import secrets
        from core.pairing import can_accept_phone, phones
        laptop_id=self.config['pairing']['laptop_id']; requests=self.db.child('pair_requests').child(laptop_id)
        def changed(event):
            try:
                data=event.data if event.path in ('/', '') else {event.path.strip('/'):event.data}
                if not isinstance(data,dict): return
                for request_id,request in data.items():
                    if not isinstance(request,dict): continue
                    secret=str(request.get('pair_secret','')); token=str(request.get('fcm_token','')); name=str(request.get('phone_name','Android phone')); auth_uid=str(request.get('auth_uid','')); requested_at=int(request.get('requested_at',0) or 0)
                    if requested_at and requested_at < int(datetime.now(timezone.utc).timestamp()*1000)-600_000: requests.child(request_id).delete(); continue
                    if not (secret and token and auth_uid and secrets.compare_digest(secret,self.config['pairing']['pair_secret']) and can_accept_phone(self.config,request_id)): continue
                    self.root.update({f'phones/{request_id}/identity':{'name':name,'auth_uid':auth_uid,'fcm_token':token,'enabled':True},f'phones/{request_id}/heartbeat':datetime.now(timezone.utc).isoformat(),f'phones/{request_id}/profile':self._default_phone_profile(),f'authorized_uids/{auth_uid}':request_id,f'pairing_status/{request_id}':{'accepted':True,'auth_uid':auth_uid}})
                    phones(self.config)[request_id]={'name':name,'enabled':True}; from core.config import save; save(self.config)
                    requests.child(request_id).delete(); self.pairing_changed.emit({'phones':self.pairing_details()['phones']})
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
                for request_id,request in data.items():
                    identity=self.root.child(f'phones/{request_id}/identity').get() or {}
                    if isinstance(request,dict) and request.get('auth_uid')==identity.get('auth_uid'): self.unlink_phone(request_id); requests.child(request_id).delete()
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
                for request_id,request in data.items():
                    identity=self.root.child(f'phones/{request_id}/identity').get() or {}
                    if isinstance(request,dict) and request.get('auth_uid')==identity.get('auth_uid') and request.get('fcm_token'):
                        self.root.child(f'phones/{request_id}/identity/fcm_token').set(str(request['fcm_token'])); requests.child(request_id).delete()
            except Exception: logging.getLogger(__name__).exception('FCM token refresh processing failed')
        try: self._token_listener=requests.listen(changed)
        except Exception as exc: logging.getLogger(__name__).warning('Token refresh listener unavailable: %s',exc)
    def pairing_details(self):
        pairing=self.config['pairing']; return {'laptop_id':pairing['laptop_id'],'pair_secret':pairing['pair_secret'],'max_phones':pairing.get('max_phones',1),'phones':pairing.get('phones',{})}
    def set_phone_limit(self, limit):
        self.config['pairing']['max_phones']=max(1,min(5,int(limit))); from core.config import save; save(self.config); self.pairing_changed.emit({'phones':self.pairing_details()['phones']})
    def unlink_phone(self, phone_id):
        if self.root:
            identity=self.root.child(f'phones/{phone_id}/identity').get() or {}; auth_uid=identity.get('auth_uid','')
            self.root.child(f'phones/{phone_id}').delete(); self.root.child(f'pairing_status/{phone_id}').delete()
            if auth_uid:self.root.child(f'authorized_uids/{auth_uid}').delete()
        self.config['pairing'].setdefault('phones',{}).pop(phone_id,None); from core.config import save; save(self.config); self.pairing_changed.emit({'phones':self.pairing_details()['phones']})
    def set_phone_enabled(self, phone_id, enabled):
        if self.root:self.root.child(f'phones/{phone_id}/identity/enabled').set(bool(enabled))
        if phone_id in self.config['pairing'].setdefault('phones',{}):self.config['pairing']['phones'][phone_id]['enabled']=bool(enabled); from core.config import save; save(self.config)
        self.pairing_changed.emit({'phones':self.pairing_details()['phones']})
    def rotate_pairing_code(self):
        from core.pairing import rotate_pair_secret
        rotate_pair_secret(self.config); self.pairing_changed.emit({'phones':self.pairing_details()['phones']})
    def close(self):
        for listener_name in ('_listener','_settings_listener','_meta_listener','_phones_listener','_pair_listener','_unlink_listener','_token_listener'):
            listener=getattr(self,listener_name)
            if listener:
                try: listener.close()
                except Exception: pass
                setattr(self,listener_name,None)
    def write_alarm(self, values):
        if not self.root: return False
        try: self.root.child('raid_alarm').update(values); return True
        except Exception as exc: self._mark_unavailable(exc); return False
    def write_settings(self, values):
        if not self.root: return False
        try: self.root.child('settings').update(values); return True
        except Exception as exc: self._mark_unavailable(exc); return False
    def _phone_quiet_now(self, profile):
        if not profile.get('quiet_hours_enabled'): return False
        try:
            now=datetime.now().time(); start=datetime.strptime(profile.get('quiet_hours_start','23:00'),'%H:%M').time(); end=datetime.strptime(profile.get('quiet_hours_end','07:00'),'%H:%M').time()
            return start <= now < end if start <= end else now >= start or now < end
        except (TypeError,ValueError): return False
    def send_phone_alarm(self, triggered_at, message='Visual alert detected', force_mode=None):
        """Broadcast a shared raid event while each enabled phone receives its own profile."""
        if not self.root or not self.app: return 0
        try:
            from firebase_admin import messaging
            count=0; all_phones=self.root.child('phones').get() or {}
            for phone_id,phone in all_phones.items():
                identity=phone.get('identity',{}); profile=phone.get('profile',{}); token=identity.get('fcm_token')
                if not token or not identity.get('enabled',True): continue
                mode='silent' if force_mode=='silent' or self._phone_quiet_now(profile) else profile.get('alert_mode','critical')
                data={'event':'raid_alarm','triggered_at':str(triggered_at),'message':str(message),'mode':str(mode),'vibration':str(bool(profile.get('vibration',True))).lower(),'flash':str(bool(profile.get('screen_flash',True))).lower(),'auto_silence_minutes':str(int(profile.get('auto_silence_minutes',5))),'volume_override':str(bool(profile.get('volume_override',True))).lower(),'sound_preset':str(profile.get('sound_preset','defcon1')),'laptop_id':self.config['pairing']['laptop_id'],'phone_id':phone_id}
                messaging.send(messaging.Message(data=data,android=messaging.AndroidConfig(priority='high',ttl=3600),token=token),app=self.app); count+=1
            return count
        except Exception as exc:
            logging.getLogger(__name__).warning('FCM delivery unavailable: %s',exc); self.error.emit(str(exc)); return 0
    def log(self, entry):
        if not self.root: return False
        try: self.root.child('activity_log/entries').push(entry); return True
        except Exception as exc: self._mark_unavailable(exc); return False
    def heartbeat(self, device='laptop'):
        if not self.root: return False
        try: self.root.child('app_meta').update({f'{device}_last_seen':datetime.now(timezone.utc).isoformat()}); return True
        except Exception as exc: self._mark_unavailable(exc); return False
    def acknowledge(self, source, cooldown_until=None):
        payload={'alarm_active':False,'acknowledged':True,'acknowledged_by':source,'acknowledged_at':datetime.now(timezone.utc).isoformat()}
        if cooldown_until: payload['cooldown_until']=cooldown_until
        self.write_alarm(payload)
