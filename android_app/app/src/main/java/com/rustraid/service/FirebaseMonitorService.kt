package com.rustraid.service
import android.app.*
import android.content.*
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.google.firebase.database.*
import java.time.Instant
class FirebaseMonitorService:Service(){
 private var listener:ValueEventListener?=null
 override fun onStartCommand(i:Intent?,f:Int,id:Int):Int{
  val manager=getSystemService(NotificationManager::class.java);manager.createNotificationChannel(NotificationChannel("monitor","Raid monitoring",NotificationManager.IMPORTANCE_LOW));startForeground(8,NotificationCompat.Builder(this,"monitor").setSmallIcon(android.R.drawable.ic_popup_sync).setContentTitle("Rust Raid Alarm").setContentText("Monitoring synchronized alert state").setOngoing(true).build())
  if(listener==null){val ref=FirebaseDatabase.getInstance().getReference("raid_alarm");listener=object:ValueEventListener{
   override fun onDataChange(s:DataSnapshot){val active=s.child("alarm_active").getValue(Boolean::class.java)?:false;if(active){ContextCompat.startForegroundService(this@FirebaseMonitorService,AlarmService.intent(this@FirebaseMonitorService))}else stopService(AlarmService.intent(this@FirebaseMonitorService))}
   override fun onCancelled(e:DatabaseError){}
  };ref.addValueEventListener(listener!!)}
  FirebaseDatabase.getInstance().getReference("app_meta/phone_last_seen").setValue(Instant.now().toString());return START_STICKY
 }
 override fun onDestroy(){listener?.let{FirebaseDatabase.getInstance().getReference("raid_alarm").removeEventListener(it)};listener=null;super.onDestroy()}
 override fun onBind(i:Intent?)=null
}
