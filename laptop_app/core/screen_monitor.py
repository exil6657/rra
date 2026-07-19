"""Opt-in local visual alert detector.
Captures only the user-selected desktop rectangle. Frames remain in memory; neither pixels nor OCR
text are uploaded. A match requires a configured phrase or reference image in consecutive frames.
"""
from __future__ import annotations
import logging
from pathlib import Path
from time import sleep, monotonic
from PyQt6.QtCore import QThread, pyqtSignal
class ScreenMonitor(QThread):
    detected=pyqtSignal(dict); state_changed=pyqtSignal(str); error=pyqtSignal(str)
    def __init__(self, settings, parent=None):
        super().__init__(parent); self.settings=settings; self._running=False; self._latched=False
    def update_settings(self, settings): self.settings=settings
    def stop(self): self._running=False; self.wait(2000)
    def valid_region(self):
        r=self.settings.get('region',{}); return all(isinstance(r.get(k),int) and r[k]>=(0 if k in ('x','y') else 1) for k in ('x','y','width','height'))
    def run(self):
        try:
            import cv2, mss, numpy as np, pytesseract
            if not self.valid_region(): raise ValueError('Select a screen region before starting monitoring.')
            r=self.settings['region']; template=None; template_path=self.settings.get('template_path','')
            if template_path:
                template=cv2.imread(template_path,cv2.IMREAD_GRAYSCALE)
                if template is None: raise ValueError('The saved reference image could not be opened.')
            phrase=self.settings.get('trigger_text','').casefold().strip()
            if not phrase and template is None: raise ValueError('Enter trigger text and/or capture a reference image.')
            self._running=True; self.state_changed.emit('monitoring'); matches=0; last_ocr=0.; ocr_text=''
            with mss.mss() as grabber:
                while self._running:
                    started=monotonic(); frame=np.array(grabber.grab(r)); gray=cv2.cvtColor(frame,cv2.COLOR_BGRA2GRAY); reasons=[]
                    if template is not None and gray.shape[0]>=template.shape[0] and gray.shape[1]>=template.shape[1]:
                        score=float(cv2.minMaxLoc(cv2.matchTemplate(gray,template,cv2.TM_CCOEFF_NORMED))[1])
                        if score>=float(self.settings.get('template_threshold',.88)): reasons.append(f'image {score:.0%}')
                    if phrase and started-last_ocr>=1:
                        ocr_text=pytesseract.image_to_string(gray,config='--psm 6').casefold(); last_ocr=started
                    if phrase and phrase in ocr_text: reasons.append('text')
                    if reasons:
                        matches+=1
                        if matches>=max(1,int(self.settings.get('confirm_frames',2))) and not self._latched:
                            self._latched=True; self.detected.emit({'reason':', '.join(reasons),'ocr_text':ocr_text[:200]})
                    else: matches=0; self._latched=False
                    sleep(max(.05, int(self.settings.get('poll_interval_ms',400))/1000-(monotonic()-started)))
            self.state_changed.emit('stopped')
        except Exception as exc:
            logging.getLogger(__name__).exception('Screen monitor stopped'); self.error.emit(str(exc)); self.state_changed.emit('error')
