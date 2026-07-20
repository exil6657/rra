from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
class CooldownManager(QObject):
    changed=pyqtSignal(str, int); expired=pyqtSignal(); auto_silence=pyqtSignal()
    def __init__(self, settings):
        super().__init__(); self.settings=settings; self.until=None; self.timer=QTimer(self); self.timer.timeout.connect(self._tick); self.silence_timer=QTimer(self); self.silence_timer.setSingleShot(True); self.silence_timer.timeout.connect(self.auto_silence)
    def in_quiet_hours(self, now=None):
        if not self.settings['quiet_hours_enabled']: return False
        now=(now or datetime.now()).time()
        try:
            parse=lambda value: datetime.strptime(value,'%H:%M').time(); start,end=parse(self.settings['quiet_hours_start']),parse(self.settings['quiet_hours_end'])
        except (TypeError,ValueError): return False
        return start <= now < end if start <= end else now >= start or now < end
    def start(self, minutes=None):
        self.until=datetime.now()+timedelta(minutes=minutes or self.settings['duration_minutes']); self.timer.start(1000); self._tick()
    def start_until(self, until):
        """Use an externally synchronized UTC/ISO expiry, falling back to normal state on expiry."""
        if isinstance(until,str):
            until=datetime.fromisoformat(until.replace('Z','+00:00')).astimezone().replace(tzinfo=None)
        self.until=until; self.timer.start(1000); self._tick()
    def end(self): self.until=None; self.timer.stop(); self.changed.emit('monitoring',0)
    def arm_auto_silence(self): self.silence_timer.start(max(1,self.settings['auto_silence_minutes'])*60_000)
    def disarm_auto_silence(self): self.silence_timer.stop()
    def remaining(self): return max(0, int((self.until-datetime.now()).total_seconds())) if self.until else 0
    def _tick(self):
        remaining=self.remaining()
        if remaining: self.changed.emit('cooldown',remaining)
        else: self.end(); self.expired.emit()
