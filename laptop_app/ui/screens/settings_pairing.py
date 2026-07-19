from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QLabel,QPushButton,QPlainTextEdit,QMessageBox
from core.pairing import manual_pairing_code
from core.config import CONFIG_DIR
class PairingSettings(QWidget):
 def __init__(self,config,firebase):
  super().__init__();self.config=config;self.firebase=firebase;l=QVBoxLayout(self);title=QLabel('Phone pairing');title.setStyleSheet('font-size:20px;font-weight:800;');l.addWidget(title);self.status=QLabel();l.addWidget(self.status);self.code=QPlainTextEdit();self.code.setReadOnly(True);self.code.setMaximumHeight(70);l.addWidget(QLabel('Manual pairing code'));l.addWidget(self.code);self.qr=QLabel(alignment=Qt.AlignmentFlag.AlignCenter);l.addWidget(self.qr);self.unlink=QPushButton('Unlink current phone');self.unlink.clicked.connect(self.unlink_phone);l.addWidget(self.unlink);self.note=QLabel('Open the Android app, enter this full code, then keep the laptop app running while it verifies and accepts the request automatically. Pairing codes are private: anyone with the code can request the phone link.');self.note.setWordWrap(True);self.note.setStyleSheet('color:#FF8C00;');l.addWidget(self.note);l.addStretch();self.refresh();firebase.pairing_changed.connect(lambda _:self.refresh())
 def refresh(self):
  details=self.firebase.pairing_details();linked=bool(details['paired_phone_id']);self.status.setText('Linked phone: '+details['paired_phone_name'] if linked else 'No phone linked — pair one Android phone below.');self.unlink.setVisible(linked);code=manual_pairing_code(self.config);self.code.setPlainText(code)
  try:
   import qrcode
   CONFIG_DIR.mkdir(parents=True,exist_ok=True);path=CONFIG_DIR/'pairing_qr.png';qrcode.make(code).save(path);self.qr.setPixmap(QPixmap(str(path)).scaled(220,220,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
  except Exception:self.qr.setText('QR generation unavailable. Use the manual pairing code.')
 def unlink_phone(self):
  if QMessageBox.question(self,'Unlink phone','Stop sending alerts to the currently linked phone?')==QMessageBox.StandardButton.Yes:self.firebase.unlink_phone();self.refresh()
