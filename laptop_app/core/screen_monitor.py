"""Opt-in local visual alert detector. Frames stay in memory and never leave the device."""
from __future__ import annotations
import logging
from time import sleep, monotonic
from PyQt6.QtCore import QThread, pyqtSignal
class ScreenMonitor(QThread):
    detected=pyqtSignal(dict); state_changed=pyqtSignal(str); error=pyqtSignal(str)
    def __init__(self, settings, parent=None): super().__init__(parent); self.settings=settings; self._running=False; self._latched=False
    def update_settings(self, settings): self.settings=settings
    def stop(self): self._running=False; self.wait(2000)
    @staticmethod
    def valid_region(settings):
        r=settings.get('region',{}); return all(isinstance(r.get(k),int) and r[k]>=(0 if k in ('x','y') else 1) for k in ('x','y','width','height'))
    @staticmethod
    def evaluate_once(settings, include_ocr=True):
        """Return local diagnostic data for one frame; used by setup test and monitor loop."""
        import cv2, mss, numpy as np
        if not ScreenMonitor.valid_region(settings): raise ValueError('Select a screen region before testing.')
        r=settings['region'];
        with mss.mss() as grabber: frame=np.array(grabber.grab(r))
        gray=cv2.cvtColor(frame,cv2.COLOR_BGRA2GRAY); phrase=settings.get('trigger_text','').casefold().strip(); template_path=settings.get('template_path',''); score=None; text=''
        if template_path:
            template=cv2.imread(template_path,cv2.IMREAD_GRAYSCALE)
            if template is None: raise ValueError('The reference image could not be opened.')
            if gray.shape[0]>=template.shape[0] and gray.shape[1]>=template.shape[1]: score=float(cv2.minMaxLoc(cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED))[1])
        if phrase and include_ocr:
            try:
                import pytesseract; text=pytesseract.image_to_string(gray,config='--psm 6').strip()
            except Exception as exc: raise RuntimeError('OCR is unavailable. Install Tesseract and add it to PATH.') from exc
        text_match=bool(phrase and phrase in text.casefold()); image_match=bool(score is not None and score>=float(settings.get('template_threshold',.88)))
        return {'matched':text_match or image_match,'text_match':text_match,'image_match':image_match,'template_score':score,'ocr_text':text[:500]}
    def run(self):
        try:
            if not self.valid_region(self.settings): raise ValueError('Select a screen region before starting monitoring.')
            phrase=self.settings.get('trigger_text','').strip(); template=self.settings.get('template_path','')
            if not phrase and not template: raise ValueError('Enter trigger text and/or capture a reference image.')
            self._running=True; self.state_changed.emit('monitoring'); matches=0; last_ocr=0.; last_result={}
            while self._running:
                started=monotonic(); include_ocr=not phrase or started-last_ocr>=1
                result=self.evaluate_once(self.settings,include_ocr=include_ocr)
                if include_ocr and phrase:last_ocr=started;last_result=result
                elif phrase:result['text_match']=last_result.get('text_match',False);result['ocr_text']=last_result.get('ocr_text','');result['matched']=result['image_match'] or result['text_match']
                if result['matched']:
                    matches+=1
                    if matches>=max(1,int(self.settings.get('confirm_frames',2))) and not self._latched:self._latched=True;self.detected.emit({'reason':'text' if result['text_match'] else f"image {result['template_score']:.0%}",'ocr_text':result['ocr_text']})
                else: matches=0; self._latched=False
                sleep(max(.05,int(self.settings.get('poll_interval_ms',400))/1000-(monotonic()-started)))
            self.state_changed.emit('stopped')
        except Exception as exc: logging.getLogger(__name__).exception('Screen monitor stopped');self.error.emit(str(exc));self.state_changed.emit('error')
class ScreenProbe(QThread):
    completed=pyqtSignal(dict); failed=pyqtSignal(str)
    def __init__(self, settings): super().__init__();self.settings=dict(settings)
    def run(self):
        try:self.completed.emit(ScreenMonitor.evaluate_once(self.settings))
        except Exception as exc:self.failed.emit(str(exc))
