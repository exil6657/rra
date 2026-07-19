from pathlib import Path
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QGuiApplication, QPixmap
from core.screen_monitor import ScreenProbe
from PyQt6.QtWidgets import QWidget,QFormLayout,QLineEdit,QPushButton,QLabel,QVBoxLayout,QSpinBox,QDoubleSpinBox,QCheckBox,QRubberBand,QMessageBox
class RegionPicker(QWidget):
    selected=pyqtSignal(dict)
    def __init__(self):
        super().__init__(None,Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint); self.setWindowState(Qt.WindowState.WindowFullScreen); self.setWindowOpacity(.35); self.origin=None; self.band=QRubberBand(QRubberBand.Shape.Rectangle,self); self.setCursor(Qt.CursorShape.CrossCursor); self.show()
    def mousePressEvent(self,e): self.origin=e.position().toPoint(); self.band.setGeometry(QRect(self.origin,self.origin));self.band.show()
    def mouseMoveEvent(self,e): self.band.setGeometry(QRect(self.origin,e.position().toPoint()).normalized())
    def mouseReleaseEvent(self,e):
        r=self.band.geometry(); self.selected.emit({'x':r.x(),'y':r.y(),'width':r.width(),'height':r.height()}); self.close()
class DiscordSettings(QWidget):
    """Legacy module name; now contains the local screen-monitor setup."""
    def __init__(self,config,save):
        super().__init__(); self.config=config;self.save=save;self.region=config['screen_monitor']['region'];v=QVBoxLayout(self);v.addWidget(QLabel('Local screen alert monitor'));v.addWidget(QLabel('Select exactly the part of your screen containing the visible Discord notification/banner. Only that rectangle is captured locally; nothing is sent to Discord or uploaded.',styleSheet='color:#00A8FF'))
        f=QFormLayout();self.enabled=QCheckBox('Enable local screen monitor');self.enabled.setChecked(config['screen_monitor'].get('enabled',False));v.addWidget(self.enabled);self.text=QLineEdit(config['screen_monitor']['trigger_text']);self.text.setPlaceholderText('Example: your display name or @username');self.interval=QSpinBox();self.interval.setRange(100,5000);self.interval.setValue(config['screen_monitor']['poll_interval_ms']);self.confirm=QSpinBox();self.confirm.setRange(1,10);self.confirm.setValue(config['screen_monitor']['confirm_frames']);self.threshold=QDoubleSpinBox();self.threshold.setRange(.50,.99);self.threshold.setSingleStep(.01);self.threshold.setValue(config['screen_monitor'].get('template_threshold',.88));self.region_label=QLabel(self.describe());f.addRow('Trigger phrase (OCR)',self.text);f.addRow('Check interval (ms)',self.interval);f.addRow('Matching frames required',self.confirm);f.addRow('Image-match threshold',self.threshold);f.addRow('Selected region',self.region_label);v.addLayout(f)
        select=QPushButton('Select screen rectangle');select.clicked.connect(self.pick);capture=QPushButton('Capture current region as reference image');capture.clicked.connect(self.capture);test=QPushButton('Test selected region now');test.clicked.connect(self.test_region);saveb=QPushButton('Save monitor settings');saveb.setObjectName('success');saveb.clicked.connect(self.commit);v.addWidget(select);v.addWidget(capture);v.addWidget(test);self.test_result=QLabel('Run a local test after selecting a region.');self.test_result.setWordWrap(True);v.addWidget(self.test_result);v.addWidget(saveb);v.addStretch()
    def describe(self): r=self.region;return f"x={r['x']}, y={r['y']}, {r['width']}×{r['height']}" if r['width'] else 'Not selected'
    def pick(self): self.picker=RegionPicker();self.picker.selected.connect(self.set_region)
    def set_region(self,r): self.region=r;self.region_label.setText(self.describe())
    def capture(self):
        if not self.region['width']: return QMessageBox.warning(self,'Region required','Select a screen rectangle first.')
        p=Path(__file__).resolve().parents[2]/'assets'/'reference.png'; screen=QGuiApplication.primaryScreen();pix=screen.grabWindow(0,self.region['x'],self.region['y'],self.region['width'],self.region['height']);pix.save(str(p),'PNG');self.commit(template_path=str(p));QMessageBox.information(self,'Reference saved','The current selected image is now a local visual trigger.')
    def test_region(self):
        settings=dict(self.config['screen_monitor']);settings.update({'enabled':self.enabled.isChecked(),'region':self.region,'trigger_text':self.text.text().strip(),'poll_interval_ms':self.interval.value(),'confirm_frames':self.confirm.value(),'template_threshold':self.threshold.value()});self.test_result.setText('Testing selected pixels locally…');self.probe=ScreenProbe(settings);self.probe.completed.connect(self.show_test);self.probe.failed.connect(lambda error:self.test_result.setText('Test failed: '+error));self.probe.start()
    def show_test(self,result):
        score='none' if result['template_score'] is None else f"{result['template_score']:.1%}";ocr=result['ocr_text'].replace('\n',' ') or 'No OCR text read';self.test_result.setText(('MATCH ✓' if result['matched'] else 'No match')+f' | image score: {score} | OCR: {ocr[:220]}')
    def commit(self,template_path=None):
        current=self.config['screen_monitor'];values={'enabled':self.enabled.isChecked(),'region':self.region,'trigger_text':self.text.text().strip(),'template_path':template_path if template_path is not None else current.get('template_path',''),'poll_interval_ms':self.interval.value(),'confirm_frames':self.confirm.value(),'template_threshold':self.threshold.value()};current.update(values);self.save('screen_monitor',values)
