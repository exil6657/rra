import logging, threading
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal
class AlarmEngine(QObject):
    active_changed=pyqtSignal(bool)
    def __init__(self, config, overlay):
        super().__init__(); self.config=config; self.overlay=overlay; self.sound=None; self.active=False; self.tts_stop=threading.Event()
        try:
            import pygame; pygame.mixer.init(); self.pygame=pygame
        except Exception as e: logging.warning('Audio disabled: %s',e); self.pygame=None
    def trigger(self, preset=None, force_stealth=False):
        alarm=self.config['alarm']; preset='stealth' if force_stealth else (preset or alarm['active_preset']); self.active=True
        if alarm['device_target'] in ('laptop','both') and preset != 'stealth':
            self._sound(preset); self._tts(alarm['custom_tts'] if preset=='custom' else 'Wake up. Raid alert.',loop=(preset=='defcon1'))
            if alarm['screen_flash']: self.overlay.start(alarm['flash_color'])
        self.active_changed.emit(True)
    def _sound(self,preset):
        if not self.pygame:return
        names={'defcon1':'defcon1.wav','tactical':'tactical.wav','stealth':'stealth.wav','custom':self.config['alarm']['custom_sound']}; path=Path(names.get(preset,''));path=path if path.is_absolute() else Path(__file__).parents[1]/'assets'/'sounds'/path
        if path.exists():self.sound=self.pygame.mixer.Sound(str(path));self.sound.set_volume(self.config['alarm']['volume']/100);self.sound.play(loops=-1)
        else:logging.warning('Alarm sound not found: %s',path)
    def _tts(self,text,loop=False):
        if not self.config['alarm']['tts_enabled']:return
        self.tts_stop.clear()
        def speak():
            try:
                import pyttsx3; engine=pyttsx3.init()
                while not self.tts_stop.is_set():
                    engine.say(text);engine.runAndWait()
                    if not loop:break
                    self.tts_stop.wait(1.0)
            except Exception:logging.exception('TTS failed')
        threading.Thread(target=speak,daemon=True,name='AlarmTTS').start()
    def stop(self):
        self.active=False;self.tts_stop.set()
        if self.sound:self.sound.stop();self.sound=None
        self.overlay.stop();self.active_changed.emit(False)
