from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QFormLayout,QComboBox,QSlider,QCheckBox,QLineEdit,QPushButton,QFileDialog,QColorDialog,QMessageBox,QLabel
class AlarmSettings(QWidget):
 test_requested=pyqtSignal(str)
 def __init__(self,c,save):
  super().__init__();self.c=c;self.save=save;l=QVBoxLayout(self);f=QFormLayout();a=c['alarm'];self.target=QComboBox();self.target.addItems(['laptop','phone','both']);self.target.setCurrentText(a['device_target']);self.preset=QComboBox();self.preset.addItems(['defcon1','tactical','stealth','custom']);self.preset.setCurrentText(a['active_preset']);self.volume=QSlider(Qt.Orientation.Horizontal);self.volume.setRange(0,100);self.volume.setValue(a['volume']);self.tts=QCheckBox('Enable text-to-speech');self.tts.setChecked(a['tts_enabled']);self.flash=QCheckBox('Enable screen flash');self.flash.setChecked(a['screen_flash']);self.message=QLineEdit(a['custom_tts']);self.custom=QLineEdit(a['custom_sound']);pick=QPushButton('Choose sound file');pick.clicked.connect(self.choose);color=QPushButton('Choose flash color');color.clicked.connect(self.choose_color);test=QPushButton('▶ Run 8-second wake test');test.setObjectName('danger');test.clicked.connect(self.request_test);f.addRow('Device target',self.target);f.addRow('Preset',self.preset);f.addRow('Volume',self.volume);f.addRow(self.tts);f.addRow(self.flash);f.addRow('Custom TTS',self.message);f.addRow('Custom WAV/MP3',self.custom);f.addRow('',pick);f.addRow('',color);f.addRow('',test);l.addLayout(f);l.addWidget(QLabel('Wake test note: set a comfortable safe volume before testing. DEFCON uses alternating pulsed tones and repeat TTS.',styleSheet='color:#FF8C00'));[x.connect(self.commit) for x in (self.target.currentTextChanged,self.preset.currentTextChanged,self.volume.valueChanged,self.tts.toggled,self.flash.toggled,self.message.editingFinished,self.custom.editingFinished)];l.addStretch()
 def choose(self):
  p,_=QFileDialog.getOpenFileName(self,'Choose alarm sound','','Audio (*.wav *.mp3)')
  if p:self.custom.setText(p);self.commit()
 def choose_color(self):
  color=QColorDialog.getColor()
  if color.isValid():self.save_values({'flash_color':color.name()})
 def request_test(self):
  if QMessageBox.question(self,'Run wake test','This plays the selected alarm at the configured application volume for 8 seconds. Continue?')==QMessageBox.StandardButton.Yes:self.test_requested.emit(self.preset.currentText())
 def save_values(self,extra={}):self.save('alarm',{'device_target':self.target.currentText(),'active_preset':self.preset.currentText(),'volume':self.volume.value(),'tts_enabled':self.tts.isChecked(),'screen_flash':self.flash.isChecked(),'custom_tts':self.message.text(),'custom_sound':self.custom.text(),**extra})
 def commit(self):self.save_values()
