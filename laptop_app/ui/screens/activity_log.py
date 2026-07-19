from pathlib import Path
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QScrollArea,QFrame,QLabel,QFileDialog,QMessageBox
class ActivityLog(QWidget):
 clear_requested=pyqtSignal()
 def __init__(self,config):
  super().__init__();self.entries=list(config.get('activity',[]));self.filter='All';root=QVBoxLayout(self);top=QHBoxLayout()
  for name in ('All','Alerts','Acknowledged','Cooldown','System','Errors'):
   button=QPushButton(name);button.clicked.connect(lambda _,value=name:self.set_filter(value));top.addWidget(button)
  top.addStretch();export=QPushButton('Export Log as .txt');export.clicked.connect(self.export);clear=QPushButton('Clear Log');clear.clicked.connect(self.request_clear);top.addWidget(export);top.addWidget(clear);root.addLayout(top);self.scroll=QScrollArea();self.scroll.setWidgetResizable(True);self.container=QWidget();self.rows=QVBoxLayout(self.container);self.rows.setAlignment(Qt.AlignmentFlag.AlignTop);self.scroll.setWidget(self.container);root.addWidget(self.scroll);self.refresh()
 def set_entries(self,entries):self.entries=list(entries);self.refresh()
 def add_record(self,record):self.entries.append(record);self.refresh()
 def set_filter(self,value):self.filter=value;self.refresh()
 def event_style(self,record):
  lower=record.lower()
  if 'alert detected' in lower:return ('🚨','#FF2D2D','alert')
  if 'acknowledged' in lower:return ('✓','#00FF88','acknowledged')
  if 'cooldown' in lower:return ('⏱','#FF8C00','cooldown')
  if 'error' in lower or 'failed' in lower:return ('⚠','#A0A0A0','error')
  return ('ℹ','#00A8FF','system')
 def visible(self,record):
  _,_,kind=self.event_style(record);return self.filter=='All' or self.filter.lower().rstrip('s')==kind
 def refresh(self):
  while self.rows.count():
   item=self.rows.takeAt(0);widget=item.widget();widget.deleteLater() if widget else None
  matches=[record for record in reversed(self.entries) if self.visible(record)]
  if not matches:self.rows.addWidget(QLabel('No matching activity recorded.',alignment=Qt.AlignmentFlag.AlignCenter));return
  for record in matches:
   icon,color,_=self.event_style(record);card=QFrame();card.setStyleSheet(f'QFrame {{background:#141414;border-left:4px solid {color};border-radius:7px;}}');layout=QHBoxLayout(card);layout.addWidget(QLabel(icon,styleSheet=f'font-size:18px;color:{color};'));timestamp,_,text=record.partition('  ');time=QLabel(timestamp);time.setStyleSheet('font-family:Consolas,monospace;color:#A0A0A0;');layout.addWidget(time);description=QLabel(text or record);description.setWordWrap(True);layout.addWidget(description,1);self.rows.addWidget(card)
 def export(self):
  path,_=QFileDialog.getSaveFileName(self,'Export activity log','rust-raid-activity.txt','Text files (*.txt)')
  if path:Path(path).write_text('\n'.join(reversed(self.entries)),encoding='utf-8')
 def request_clear(self):
  if QMessageBox.question(self,'Clear activity log','Remove all local activity records?')==QMessageBox.StandardButton.Yes:self.clear_requested.emit()
