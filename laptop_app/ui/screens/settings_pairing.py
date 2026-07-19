from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QPlainTextEdit,QSpinBox,QCheckBox,QFrame,QMessageBox
from core.pairing import manual_pairing_code
from core.config import CONFIG_DIR
class PairingSettings(QWidget):
 def __init__(self,config,firebase):
  super().__init__();self.config=config;self.firebase=firebase;l=QVBoxLayout(self);title=QLabel('Phone fleet');title.setStyleSheet('font-size:20px;font-weight:800;');l.addWidget(title);self.status=QLabel();l.addWidget(self.status);limit_row=QHBoxLayout();limit_row.addWidget(QLabel('Maximum linked phones'));self.limit=QSpinBox();self.limit.setRange(1,5);self.limit.valueChanged.connect(lambda value:self.firebase.set_phone_limit(value));limit_row.addWidget(self.limit);limit_row.addStretch();l.addLayout(limit_row);self.code=QPlainTextEdit();self.code.setReadOnly(True);self.code.setMaximumHeight(70);l.addWidget(QLabel('Pairing code'));l.addWidget(self.code);self.qr=QLabel(alignment=Qt.AlignmentFlag.AlignCenter);l.addWidget(self.qr);self.phones_box=QVBoxLayout();l.addLayout(self.phones_box);self.rotate=QPushButton('Generate new pairing code');self.rotate.clicked.connect(self.rotate_code);l.addWidget(self.rotate);self.note=QLabel('Each linked phone controls its own alarm profile. The PC broadcasts the raid event to all enabled phones. Pairing codes are private.');self.note.setWordWrap(True);self.note.setStyleSheet('color:#FF8C00;');l.addWidget(self.note);l.addStretch();self.refresh();firebase.pairing_changed.connect(lambda _:self.refresh());firebase.remote_phones.connect(lambda _:self.refresh())
 def refresh(self):
  details=self.firebase.pairing_details();phones=details.get('phones',{});self.limit.blockSignals(True);self.limit.setValue(details.get('max_phones',1));self.limit.blockSignals(False);self.status.setText(f'{len(phones)}/{details.get("max_phones",1)} phone(s) linked');self.code.setPlainText(manual_pairing_code(self.config))
  try:
   import qrcode
   CONFIG_DIR.mkdir(parents=True,exist_ok=True);path=CONFIG_DIR/'pairing_qr.png';qrcode.make(self.code.toPlainText()).save(path);self.qr.setPixmap(QPixmap(str(path)).scaled(190,190,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
  except Exception:self.qr.setText('QR generation unavailable. Use the manual pairing code.')
  while self.phones_box.count():
   item=self.phones_box.takeAt(0);widget=item.widget();widget.deleteLater() if widget else None
  if not phones:self.phones_box.addWidget(QLabel('No phones paired yet.'))
  for phone_id,phone in phones.items():
   card=QFrame();card.setStyleSheet('background:#141414;border:1px solid #2A2A2A;border-radius:8px;');row=QHBoxLayout(card);enabled=QCheckBox(phone.get('name','Phone'));enabled.setChecked(phone.get('enabled',True));profile=phone.get('profile',{});summary=QLabel(f"{profile.get('alert_mode','critical').upper()} // {profile.get('sound_preset','defcon1').upper()} // {'FLASH' if profile.get('screen_flash',True) else 'NO FLASH'}");enabled.toggled.connect(lambda value,pid=phone_id:self.firebase.set_phone_enabled(pid,value));remove=QPushButton('Remove');remove.clicked.connect(lambda _,pid=phone_id:self.remove_phone(pid));row.addWidget(enabled,1);row.addWidget(summary,1);row.addWidget(remove);self.phones_box.addWidget(card)
 def rotate_code(self):
  if QMessageBox.question(self,'Generate new pairing code','Invalidate the currently displayed pairing code? Pending pairing requests using it will no longer work.')==QMessageBox.StandardButton.Yes:self.firebase.rotate_pairing_code();self.refresh()
 def remove_phone(self,phone_id):
  if QMessageBox.question(self,'Remove phone','Stop this phone receiving future PC alerts?')==QMessageBox.StandardButton.Yes:self.firebase.unlink_phone(phone_id);self.refresh()
