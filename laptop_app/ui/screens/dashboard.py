from datetime import datetime
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QLabel,QPushButton,QFrame
from ui.components.status_indicator import StatusIndicator
from ui.components.cooldown_ring import CooldownRing
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
        grid.addWidget(self.card('Quick Settings',quick),1,0); self.firebase_health='unavailable';self.phone_health='unknown';self.summary=QLabel();self.cooldown_ring=CooldownRing();self.refresh_summary('monitoring',0); status_row=QHBoxLayout();status_row.addWidget(self.cooldown_ring);status_row.addWidget(self.summary,1);summary_card=self.card('Current Status Summary',[self.summary]);summary_layout=summary_card.layout();summary_layout.removeWidget(self.summary);summary_layout.addLayout(status_row);grid.addWidget(summary_card,1,1)
        l.addWidget(QLabel('ACTIVITY (latest 5)')); self.events=QLabel('No events yet'); self.events.setStyleSheet('padding:12px;background:#141414'); l.addWidget(self.events); l.addStretch()
    def card(self,title,widgets):
        f=QFrame(); f.setProperty('class','card'); v=QVBoxLayout(f); h=QLabel(title); h.setStyleSheet('font-weight:800;font-size:17px'); v.addWidget(h)
        for w in widgets: v.addWidget(w)
        return f
    def refresh_summary(self,state='monitoring',seconds=0):
        cooldown=f'{seconds//3600:02}:{seconds%3600//60:02}:{seconds%60:02}' if state=='cooldown' else 'inactive';self.cooldown_ring.set_remaining(seconds if state=='cooldown' else 0,self.config['cooldown']['duration_minutes']*60);quiet='enabled' if self.config['cooldown'].get('quiet_hours_enabled') else 'off';self.summary.setText(f'Cooldown: {cooldown}\nQuiet hours: {quiet}\nFirebase: {self.firebase_health}\nPhone: {self.phone_health}')
    def set_health(self,firebase=None,phone=None):
        if firebase is not None:self.firebase_health=firebase
        if phone is not None:self.phone_health=phone
        self.refresh_summary()
    def set_state(self,state,seconds=0):
        colors={'monitoring':'#063B25','raid':'#650B0B','cooldown':'#593400','disconnected':'#242424'}; texts={'monitoring':'🟢 MONITORING','raid':'🚨 RAID DETECTED','cooldown':f'⏱ COOLDOWN ACTIVE — {seconds//3600:02}:{seconds%3600//60:02}:{seconds%60:02}','disconnected':'⚠️ DISCONNECTED — Reconnecting…'}
        self.banner.setText(texts[state]); self.refresh_summary(state,seconds); self.banner.setStyleSheet(f'background:{colors[state]};padding:18px;border-radius:10px'); self.ack.setVisible(state=='raid'); self.over.setVisible(state=='cooldown'); self.status.set_color({'monitoring':'#00FF88','raid':'#FF2D2D','cooldown':'#FF8C00','disconnected':'#A0A0A0'}[state]); self.connection.setText('Connected' if state=='monitoring' else state.title())
    def add_event(self,text): self.events.setText(datetime.now().strftime('%H:%M:%S')+'  '+text+'\n'+self.events.text())
