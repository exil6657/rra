from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QPushButton,QLabel
class Sidebar(QWidget):
    selected=pyqtSignal(str)
    def __init__(self):
        super().__init__();self.setObjectName('sidebar');self.setFixedWidth(190);layout=QVBoxLayout(self);layout.setContentsMargins(14,24,14,18);layout.setSpacing(6)
        brand=QLabel('RUST RAID');brand.setObjectName('brand');layout.addWidget(brand);sub=QLabel('// PC COMMAND LINK');sub.setObjectName('terminal');layout.addWidget(sub);layout.addSpacing(20)
        for label,key in [('◈  DASHBOARD','dashboard'),('⚙  CONFIGURATION','settings'),('☷  ACTIVITY LOG','log'),('ⓘ  ABOUT','about')]:
            button=QPushButton(label);button.setProperty('role','nav');button.clicked.connect(lambda _,route=key:self.selected.emit(route));layout.addWidget(button)
        layout.addStretch();footer=QLabel('SECURE PAIR LINK\nLOCAL SCREEN MONITOR');footer.setObjectName('terminal');layout.addWidget(footer)
