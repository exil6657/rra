from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QTextEdit,QPushButton,QComboBox
from pathlib import Path
class ActivityLog(QWidget):
 def __init__(self,config):
  super().__init__();self.config=config;l=QVBoxLayout(self);h=QHBoxLayout();self.filter=QComboBox();self.filter.addItems(['All','Raids','System','Errors']);export=QPushButton('Export Log as .txt');export.clicked.connect(self.export);h.addWidget(self.filter);h.addWidget(export);l.addLayout(h);self.view=QTextEdit();self.view.setReadOnly(True);l.addWidget(self.view);self.refresh()
 def refresh(self):self.view.setPlainText('\n'.join(reversed(self.config.get('activity',[]))))
 def export(self):Path('activity-log.txt').write_text(self.view.toPlainText(),encoding='utf-8')
