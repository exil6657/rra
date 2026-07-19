package com.rustraid.service
import android.app.*
import android.content.*
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.database.*
import com.rustraid.data.FirebaseSession
import com.rustraid.data.PairingManager
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.first
import java.time.Instant
class FirebaseMonitorService:Service(){
 private var listener:ValueEventListener?=null;private var laptopId="";private val scope=CoroutineScope(SupervisorJob()+Dispatchers.IO)
 override fun onStartCommand(i:Intent?,f:Int,id:Int):Int{
  val manager=getSystemService(NotificationManager::class.java);manager.createNotificationChannel(NotificationChannel("monitor","Raid monitoring",NotificationManager.IMPORTANCE_LOW));startForeground(8,NotificationCompat.Builder(this,"monitor").setSmallIcon(android.R.drawable.ic_popup_sync).setContentTitle("Rust Raid Alarm").setContentText("Monitoring linked laptop").setOngoing(true).build())
  scope.launch {val pairing=PairingManager(this@FirebaseMonitorService).info.first();if(!pairing.linked){stopSelf();return@launch};laptopId=pairing.laptopId;if(FirebaseAuth.getInstance().currentUser==null){FirebaseSession.ensureAuthenticated({startService(Intent(this@FirebaseMonitorService,FirebaseMonitorService::class.java))},{});return@launch};withContext(Dispatchers.Main){startListener()}}
  return START_STICKY
 }
 private fun startListener(){if(listener!=null||laptopId.isBlank())return;val ref=FirebaseDatabase.getInstance().getReference("laptops").child(laptopId).child("raid_alarm");listener=object:ValueEventListener{override fun onDataChange(s:DataSnapshot){val active=s.child("alarm_active").getValue(Boolean::class.java)?:false;val target=s.child("device_target").getValue(String::class.java)?:"both";if(active&&(target=="phone"||target=="both"))ContextCompat.startForegroundService(this@FirebaseMonitorService,AlarmService.intent(this@FirebaseMonitorService,s.child("alert_mode").getValue(String::class.java)=="silent",s.child("phone_vibration").getValue(Boolean::class.java)?:true,s.child("phone_screen_flash").getValue(Boolean::class.java)?:true,laptopId)) else stopService(AlarmService.intent(this@FirebaseMonitorService,laptopId=laptopId))};override fun onCancelled(e:DatabaseError){}};ref.addValueEventListener(listener!!);FirebaseDatabase.getInstance().getReference("laptops").child(laptopId).child("app_meta/phone_last_seen").setValue(Instant.now().toString())}
 override fun onDestroy(){listener?.let{FirebaseDatabase.getInstance().getReference("laptops").child(laptopId).child("raid_alarm").removeEventListener(it)};scope.cancel();super.onDestroy()}
 override fun onBind(i:Intent?)=null
}
