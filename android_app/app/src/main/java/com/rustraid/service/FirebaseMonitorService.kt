package com.rustraid.service
import android.app.*
import android.content.*
import android.os.Handler
import android.os.Looper
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.database.*
import com.rustraid.data.FirebaseRepository
import com.rustraid.data.FirebaseSession
import com.rustraid.data.PairingManager
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.first
import java.time.LocalTime
import java.time.format.DateTimeFormatter

class FirebaseMonitorService:Service(){
 private var alarmListener:ValueEventListener?=null;private var profileListener:ValueEventListener?=null;private var laptopId="";private var phoneId="";private var profile:DataSnapshot?=null
 private val heartbeatHandler=Handler(Looper.getMainLooper());private val heartbeat=object:Runnable{override fun run(){if(laptopId.isNotBlank()&&phoneId.isNotBlank()){FirebaseRepository(laptopId,phoneId).heartbeat();heartbeatHandler.postDelayed(this,60_000)}}};private val scope=CoroutineScope(SupervisorJob()+Dispatchers.IO)
 override fun onStartCommand(i:Intent?,f:Int,id:Int):Int{
  val manager=getSystemService(NotificationManager::class.java);manager.createNotificationChannel(NotificationChannel("monitor","Raid monitoring",NotificationManager.IMPORTANCE_LOW));startForeground(8,NotificationCompat.Builder(this,"monitor").setSmallIcon(android.R.drawable.ic_popup_sync).setContentTitle("Rust Raid Alarm").setContentText("Monitoring linked PC").setOngoing(true).build())
  scope.launch {val pairing=PairingManager(this@FirebaseMonitorService).info.first();if(!pairing.linked){stopSelf();return@launch};laptopId=pairing.laptopId;phoneId=pairing.phoneId;if(FirebaseAuth.getInstance().currentUser==null){FirebaseSession.ensureAuthenticated({startService(Intent(this@FirebaseMonitorService,FirebaseMonitorService::class.java))},{});return@launch};withContext(Dispatchers.Main){startListeners()}}
  return START_STICKY
 }
 private fun profileQuiet(p:DataSnapshot?):Boolean{if(p?.child("quiet_hours_enabled")?.getValue(Boolean::class.java)!=true)return false;return runCatching{val f=DateTimeFormatter.ofPattern("HH:mm");val now=LocalTime.now();val start=LocalTime.parse(p.child("quiet_hours_start").getValue(String::class.java)?:"23:00",f);val end=LocalTime.parse(p.child("quiet_hours_end").getValue(String::class.java)?:"07:00",f);if(start<=end)now>=start&&now<end else now>=start||now<end}.getOrDefault(false)}
 private fun startListeners(){if(alarmListener!=null||laptopId.isBlank()||phoneId.isBlank())return;val base=FirebaseDatabase.getInstance().getReference("laptops").child(laptopId);profileListener=object:ValueEventListener{override fun onDataChange(s:DataSnapshot){profile=s};override fun onCancelled(e:DatabaseError){}};base.child("phones").child(phoneId).child("profile").addValueEventListener(profileListener!!);alarmListener=object:ValueEventListener{override fun onDataChange(s:DataSnapshot){val active=s.child("alarm_active").getValue(Boolean::class.java)?:false;val target=s.child("device_target").getValue(String::class.java)?:"both";val p=profile;val silent=(s.child("force_silent").getValue(Boolean::class.java)?:false)||(p?.child("alert_mode")?.getValue(String::class.java)=="silent")||profileQuiet(p);if(active&&(target=="phone"||target=="both"))ContextCompat.startForegroundService(this@FirebaseMonitorService,AlarmService.intent(this@FirebaseMonitorService,silent,p?.child("vibration")?.getValue(Boolean::class.java)?:true,p?.child("screen_flash")?.getValue(Boolean::class.java)?:true,laptopId,(p?.child("auto_silence_minutes")?.getValue(Long::class.java)?:5L).toInt(),p?.child("volume_override")?.getValue(Boolean::class.java)?:true,p?.child("sound_preset")?.getValue(String::class.java)?:"defcon1")) else stopService(AlarmService.intent(this@FirebaseMonitorService,laptopId=laptopId))};override fun onCancelled(e:DatabaseError){}};base.child("raid_alarm").addValueEventListener(alarmListener!!);heartbeatHandler.removeCallbacks(heartbeat);heartbeatHandler.post(heartbeat)}
 override fun onDestroy(){val base=FirebaseDatabase.getInstance().getReference("laptops").child(laptopId);alarmListener?.let{base.child("raid_alarm").removeEventListener(it)};profileListener?.let{base.child("phones").child(phoneId).child("profile").removeEventListener(it)};heartbeatHandler.removeCallbacks(heartbeat);scope.cancel();super.onDestroy()}
 override fun onBind(i:Intent?)=null
}
