from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QTextEdit,QPushButton,QComboBox,QMessageBox,QFileDialog
from pathlib import Path
from core.config import save
class ActivityLog(QWidget):
 def __init__(self,config):
  super().__init__();self.config=config;l=QVBoxLayout(self);h=QHBoxLayout();self.filter=QComboBox();self.filter.addItems(['All','Alerts','System','Errors']);self.filter.currentTextChanged.connect(self.refresh);export=QPushButton('Export Log as .txt');export.clicked.connect(self.export);clear=QPushButton('Clear Log');clear.clicked.connect(self.clear);h.addWidget(self.filter);h.addStretch();h.addWidget(export);h.addWidget(clear);l.addLayout(h);self.view=QTextEdit();self.view.setReadOnly(True);l.addWidget(self.view);self.refresh()
 def refresh(self):
  items=reversed(self.config.get('activity',[]));choice=self.filter.currentText().lower();rows=[x for x in items if choice=='all' or choice[:-1] in x.lower()];self.view.setPlainText('\n'.join(rows) or 'No activity recorded.')
 def export(self):
  path,_=QFileDialog.getSaveFileName(self,'Export activity log','rust-raid-activity.txt','Text files (*.txt)')
  if path:Path(path).write_text(self.view.toPlainText(),encoding='utf-8')
 def clear(self):
  if QMessageBox.question(self,'Clear activity log','Remove all local activity records?')==QMessageBox.StandardButton.Yes:self.config['activity']=[];save(self.config);self.refresh()
