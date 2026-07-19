from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor,QPainter,QPen,QFont
from PyQt6.QtWidgets import QWidget
class CooldownRing(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent);self.progress=0.0;self.seconds=0;self.setFixedSize(104,104)
    def set_remaining(self,seconds,total_seconds):
        self.seconds=max(0,seconds);self.progress=self.seconds/max(1,total_seconds);self.update()
    def paintEvent(self,event):
        painter=QPainter(self);painter.setRenderHint(QPainter.RenderHint.Antialiasing);rect=self.rect().adjusted(8,8,-8,-8)
        painter.setPen(QPen(QColor('#2A2A2A'),8));painter.drawArc(rect,0,360*16)
        painter.setPen(QPen(QColor('#FF8C00'),8,cap=Qt.PenCapStyle.RoundCap));painter.drawArc(rect,90*16,-int(360*16*self.progress))
        text=f'{self.seconds//60:02}:{self.seconds%60:02}' if self.seconds else 'READY';painter.setPen(QColor('#FFFFFF'));font=QFont();font.setBold(True);font.setPointSize(10);painter.setFont(font);painter.drawText(self.rect(),Qt.AlignmentFlag.AlignCenter,text)
