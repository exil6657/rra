"""Local screen-monitor settings (legacy filename retained for compatibility)."""
from pathlib import Path
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QWidget,QFormLayout,QLineEdit,QPushButton,QLabel,QVBoxLayout,QHBoxLayout,QSpinBox,QDoubleSpinBox,QCheckBox,QRubberBand,QMessageBox,QFileDialog
from core.screen_monitor import ScreenProbe, ScreenMonitor
class RegionPicker(QWidget):
    """Transparent virtual-desktop overlay returning physical global coordinates for mss."""
    selected=pyqtSignal(dict)
    def __init__(self):
        super().__init__(None,Qt.WindowType.FramelessWindowHint|Qt.WindowType.WindowStaysOnTopHint|Qt.WindowType.Tool)
        screens=QGuiApplication.screens();bounds=screens[0].geometry()
        for screen in screens[1:]:bounds=bounds.united(screen.geometry())
        self.setGeometry(bounds);self.setWindowOpacity(.35);self.setStyleSheet('background:#00A8FF;');self.origin_global=None;self.band=QRubberBand(QRubberBand.Shape.Rectangle,self);self.setCursor(Qt.CursorShape.CrossCursor);self.show()
    def mousePressEvent(self,event):
        self.origin_global=self.mapToGlobal(event.position().toPoint());local=self.mapFromGlobal(self.origin_global);self.band.setGeometry(QRect(local,local));self.band.show()
    def mouseMoveEvent(self,event):
        current=self.mapToGlobal(event.position().toPoint());self.band.setGeometry(QRect(self.mapFromGlobal(self.origin_global),self.mapFromGlobal(current)).normalized())
    def mouseReleaseEvent(self,event):
        end=self.mapToGlobal(event.position().toPoint());rect=QRect(self.origin_global,end).normalized();self.selected.emit({'x':rect.x(),'y':rect.y(),'width':rect.width(),'height':rect.height()});self.close()
class DiscordSettings(QWidget):
    def __init__(self,config,save):
        super().__init__();self.config=config;self.save=save;self.region=config['screen_monitor']['region'];self.template_path=config['screen_monitor'].get('template_path','');root=QVBoxLayout(self);title=QLabel('Local screen alert monitor');title.setStyleSheet('font-size:20px;font-weight:800;');root.addWidget(title);description=QLabel('Choose only the visible alert/banner area. Text matching and reference-image matching are local-only. Configure either trigger, or both for additional coverage.');description.setWordWrap(True);description.setStyleSheet('color:#00A8FF');root.addWidget(description)
        form=QFormLayout();self.enabled=QCheckBox('Enable local screen monitor');self.enabled.setChecked(config['screen_monitor'].get('enabled',False));root.addWidget(self.enabled);self.text=QLineEdit(config['screen_monitor']['trigger_text']);self.text.setPlaceholderText('Example: your display name or @username');self.interval=QSpinBox();self.interval.setRange(100,5000);self.interval.setValue(config['screen_monitor']['poll_interval_ms']);self.confirm=QSpinBox();self.confirm.setRange(1,10);self.confirm.setValue(config['screen_monitor']['confirm_frames']);self.threshold=QDoubleSpinBox();self.threshold.setRange(.50,.99);self.threshold.setSingleStep(.01);self.threshold.setValue(config['screen_monitor'].get('template_threshold',.88));self.region_label=QLabel(self.describe_region());form.addRow('Trigger phrase (OCR)',self.text);form.addRow('Check interval (ms)',self.interval);form.addRow('Matching frames required',self.confirm);form.addRow('Image-match threshold',self.threshold);form.addRow('Selected region',self.region_label);root.addLayout(form)
        select=QPushButton('Select screen rectangle');select.clicked.connect(self.pick_region);root.addWidget(select)
        template_row=QHBoxLayout();capture=QPushButton('Capture current region as reference image');capture.clicked.connect(self.capture_reference);choose=QPushButton('Choose reference image');choose.clicked.connect(self.choose_reference);clear=QPushButton('Clear reference image');clear.clicked.connect(self.clear_reference);template_row.addWidget(capture);template_row.addWidget(choose);template_row.addWidget(clear);root.addLayout(template_row);self.reference_status=QLabel();self.refresh_reference_status();root.addWidget(self.reference_status)
        diagnostics=QHBoxLayout();check_ocr=QPushButton('Check OCR engine');check_ocr.clicked.connect(self.check_ocr);test=QPushButton('Test selected region now');test.clicked.connect(self.test_region);diagnostics.addWidget(check_ocr);diagnostics.addWidget(test);root.addLayout(diagnostics);self.test_result=QLabel('Run a local test after selecting a region.');self.test_result.setWordWrap(True);root.addWidget(self.test_result)
        save_button=QPushButton('Save monitor settings');save_button.setObjectName('success');save_button.clicked.connect(self.commit);root.addWidget(save_button);root.addStretch()
    def describe_region(self):return f"x={self.region['x']}, y={self.region['y']}, {self.region['width']}×{self.region['height']}" if self.region.get('width') else 'Not selected'
    def refresh_reference_status(self):
        valid=bool(self.template_path and Path(self.template_path).is_file());self.reference_status.setText('Reference image: configured ✓' if valid else 'Reference image: none — OCR phrase is required to trigger.');self.reference_status.setStyleSheet('color:#00FF88;' if valid else 'color:#A0A0A0;')
    def pick_region(self):self.picker=RegionPicker();self.picker.selected.connect(self.set_region)
    def set_region(self,region):self.region=region;self.region_label.setText(self.describe_region())
    def capture_reference(self):
        if not ScreenMonitor.valid_region({'region':self.region}):return QMessageBox.warning(self,'Region required','Select a screen rectangle first.')
        path=Path(__file__).resolve().parents[2]/'assets'/'reference.png'
        try:ScreenMonitor.save_reference({'region':self.region},path)
        except Exception as exc:return QMessageBox.warning(self,'Capture failed',str(exc))
        self.template_path=str(path);self.refresh_reference_status();self.commit();QMessageBox.information(self,'Reference saved','The current selected image is saved locally and will be used for image matching.')
    def choose_reference(self):
        path,_=QFileDialog.getOpenFileName(self,'Choose reference image','','Images (*.png *.jpg *.jpeg *.bmp)')
        if path:
            self.template_path=path;self.refresh_reference_status();self.commit()
    def clear_reference(self):
        if not self.template_path:return
        local=Path(__file__).resolve().parents[2]/'assets'/'reference.png'
        if Path(self.template_path)==local and local.exists():local.unlink()
        self.template_path='';self.refresh_reference_status();self.commit()
    def check_ocr(self):
        ready,message=ScreenMonitor.ocr_status();self.test_result.setText(message);self.test_result.setStyleSheet('color:#00FF88;' if ready else 'color:#FF8C00;')
    def current_settings(self):
        settings=dict(self.config['screen_monitor']);settings.update({'enabled':self.enabled.isChecked(),'region':self.region,'trigger_text':self.text.text().strip(),'template_path':self.template_path,'poll_interval_ms':self.interval.value(),'confirm_frames':self.confirm.value(),'template_threshold':self.threshold.value()});return settings
    def test_region(self):
        settings=self.current_settings()
        if not settings['trigger_text'] and not settings['template_path']:return self.test_result.setText('Configure an OCR phrase and/or a reference image before testing.')
        self.test_result.setStyleSheet('color:#A0A0A0;');self.test_result.setText('Testing selected pixels locally…');self.probe=ScreenProbe(settings);self.probe.completed.connect(self.show_test);self.probe.failed.connect(lambda error:self.test_result.setText('Test failed: '+error));self.probe.start()
    def show_test(self,result):
        score='none' if result['template_score'] is None else f"{result['template_score']:.1%}";ocr=result['ocr_text'].replace('\n',' ') or 'No OCR text read';self.test_result.setStyleSheet('color:#00FF88;' if result['matched'] else 'color:#FF8C00;');self.test_result.setText(('MATCH ✓' if result['matched'] else 'No match')+f' | image score: {score} | OCR: {ocr[:220]}')
    def commit(self):
        values=self.current_settings();self.config['screen_monitor'].update(values);self.save('screen_monitor',values)
