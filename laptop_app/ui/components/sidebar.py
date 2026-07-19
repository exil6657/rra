from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QPushButton,QLabel
class Sidebar(QWidget):
    selected=pyqtSignal(str)
    def __init__(self):
        super().__init__(); self.setFixedWidth(155); l=QVBoxLayout(self); l.setContentsMargins(10,20,10,20); logo=QLabel('RRA\nCOMMAND'); logo.setObjectName('title'); l.addWidget(logo)
        for label,key in [('🏠  Dashboard','dashboard'),('⚙️  Settings','settings'),('📋  Activity Log','log'),('ℹ️  About','about')]:
            b=QPushButton(label); b.clicked.connect(lambda _,k=key:self.selected.emit(k)); l.addWidget(b)
        l.addStretch(); l.addWidget(QLabel('v1.0.0\nCOMPLIANT BOT MODE'))
