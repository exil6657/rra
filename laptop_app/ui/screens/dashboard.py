from datetime import datetime
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,QFrame
from ui.components.status_indicator import StatusIndicator
class Dashboard(QWidget):
    test_requested=pyqtSignal(); acknowledge_requested=pyqtSignal(); raid_over_requested=pyqtSignal(); target_changed=pyqtSignal(str); preset_changed=pyqtSignal(str)
    def __init__(self,config):
        super().__init__(); self.config=config; l=QVBoxLayout(self); self.banner=QLabel('🟢 MONITORING — Ready to watch selected screen region'); self.banner.setObjectName('title'); self.banner.setStyleSheet('background:#063B25;padding:18px;border-radius:10px'); l.addWidget(self.banner)
        grid=QGridLayout(); l.addLayout(grid); self.status=StatusIndicator(); self.connection=QLabel('Disconnected'); grid.addWidget(self.card('Screen Monitor Status',[self.status,self.connection,QLabel('Monitoring: selected screen region'),QLabel('Last ping: Never')]),0,0)
        self.alarm_buttons=[]; test=QPushButton('🔴 TEST RAID'); test.setObjectName('danger'); test.clicked.connect(self.test_requested); self.ack=QPushButton('✅ ACKNOWLEDGE'); self.ack.setObjectName('success'); self.ack.clicked.connect(self.acknowledge_requested); self.ack.hide(); self.over=QPushButton('🏁 RAID OVER'); self.over.clicked.connect(self.raid_over_requested); self.over.hide(); grid.addWidget(self.card('Alarm Control',[QLabel('Preset: '+config['alarm']['active_preset'].upper()),test,self.ack,self.over]),0,1)
        quick=[]
        for text,key in [('Laptop Only','laptop'),('Phone Only','phone'),('Both','both')]:
            b=QPushButton(text); b.clicked.connect(lambda _,x=key:self.target_changed.emit(x)); quick.append(b)
        for text,key in [('DEFCON 1','defcon1'),('Tactical','tactical'),('Stealth','stealth'),('Custom','custom')]:
            b=QPushButton(text); b.clicked.connect(lambda _,x=key:self.preset_changed.emit(x)); quick.append(b)
        grid.addWidget(self.card('Quick Settings',quick),1,0); self.summary=QLabel('Cooldown: inactive\nFirebase: unavailable\nQuiet hours: inactive'); grid.addWidget(self.card('Current Status Summary',[self.summary]),1,1)
        l.addWidget(QLabel('ACTIVITY (latest 5)')); self.events=QLabel('No events yet'); self.events.setStyleSheet('padding:12px;background:#141414'); l.addWidget(self.events); l.addStretch()
    def card(self,title,widgets):
        f=QFrame(); f.setProperty('class','card'); v=QVBoxLayout(f); h=QLabel(title); h.setStyleSheet('font-weight:800;font-size:17px'); v.addWidget(h)
        for w in widgets: v.addWidget(w)
        return f
    def set_state(self,state,seconds=0):
        colors={'monitoring':'#063B25','raid':'#650B0B','cooldown':'#593400','disconnected':'#242424'}; texts={'monitoring':'🟢 MONITORING','raid':'🚨 RAID DETECTED','cooldown':f'⏱ COOLDOWN ACTIVE — {seconds//3600:02}:{seconds%3600//60:02}:{seconds%60:02}','disconnected':'⚠️ DISCONNECTED — Reconnecting…'}
        self.banner.setText(texts[state]); self.banner.setStyleSheet(f'background:{colors[state]};padding:18px;border-radius:10px'); self.ack.setVisible(state=='raid'); self.over.setVisible(state=='cooldown'); self.status.set_color({'monitoring':'#00FF88','raid':'#FF2D2D','cooldown':'#FF8C00','disconnected':'#A0A0A0'}[state]); self.connection.setText('Connected' if state=='monitoring' else state.title())
    def add_event(self,text): self.events.setText(datetime.now().strftime('%H:%M:%S')+'  '+text+'\n'+self.events.text())
