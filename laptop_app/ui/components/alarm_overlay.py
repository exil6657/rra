from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QWidget
class AlarmOverlay(QWidget):
    def __init__(self):
        super().__init__(None, Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents); self.setWindowOpacity(.72); self.timer=QTimer(self); self.timer.timeout.connect(self._toggle); self.on=False
    def start(self,color='#FF2D2D'):
        self.color=QColor(color); self.showFullScreen(); self.timer.start(250); self._toggle()
    def _toggle(self):
        self.on=not self.on; p=self.palette(); p.setColor(QPalette.ColorRole.Window,self.color if self.on else QColor('#0D0D0D')); self.setPalette(p); self.setAutoFillBackground(True)
    def stop(self): self.timer.stop(); self.hide()
