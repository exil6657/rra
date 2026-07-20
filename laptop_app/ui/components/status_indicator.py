from PyQt6.QtCore import QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget
class StatusIndicator(QWidget):
    def __init__(self,color='#00FF88',parent=None):
        super().__init__(parent); self.color=QColor(color); self._opacity=.45; self.setFixedSize(18,18); self.anim=QPropertyAnimation(self,b'opacity',self); self.anim.setDuration(950); self.anim.setStartValue(.25); self.anim.setEndValue(1.0); self.anim.setLoopCount(-1); self.anim.start()
    def set_color(self,color): self.color=QColor(color); self.update()
    def get_opacity(self): return self._opacity
    def set_opacity(self,v): self._opacity=v; self.update()
    opacity=pyqtProperty(float,get_opacity,set_opacity)
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing); c=QColor(self.color); c.setAlphaF(self._opacity); p.setBrush(c); p.setPen(c); p.drawEllipse(2,2,14,14)
