package com.rustraid.service
import android.app.*
import android.content.*
import android.media.*
import android.os.*
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.rustraid.AlarmActivity
import com.rustraid.R
class AlarmService:Service(){
 private var player:MediaPlayer?=null; private var wakeLock:PowerManager.WakeLock?=null
 override fun onStartCommand(i:Intent?,f:Int,id:Int):Int{
  if(player!=null) return START_NOT_STICKY
  val manager=getSystemService(NotificationManager::class.java);manager.createNotificationChannel(NotificationChannel("raid","Raid alerts",NotificationManager.IMPORTANCE_HIGH))
  val alarmIntent=PendingIntent.getActivity(this,1,Intent(this,AlarmActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
  val ackIntent=PendingIntent.getBroadcast(this,2,Intent(this,AcknowledgeReceiver::class.java),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
  val notice=NotificationCompat.Builder(this,"raid").setSmallIcon(android.R.drawable.ic_dialog_alert).setContentTitle("RAID ACTIVE").setContentText("Tap to acknowledge").setPriority(NotificationCompat.PRIORITY_MAX).setCategory(NotificationCompat.CATEGORY_ALARM).setFullScreenIntent(alarmIntent,true).setContentIntent(alarmIntent).addAction(0,"Acknowledge",ackIntent).build();startForeground(4,notice)
  val power=getSystemService(PowerManager::class.java);wakeLock=power.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"RustRaid:alarm").apply{acquire(10*60*1000L)}
  val audio=getSystemService(AudioManager::class.java);audio.setStreamVolume(AudioManager.STREAM_ALARM,audio.getStreamMaxVolume(AudioManager.STREAM_ALARM),0)
  player=MediaPlayer.create(this,R.raw.alarm_defcon)?.apply{isLooping=true;setAudioStreamType(AudioManager.STREAM_ALARM);start()};getSystemService(Vibrator::class.java).vibrate(VibrationEffect.createWaveform(longArrayOf(0,500,200,500,200,500),0));return START_NOT_STICKY
 }
 override fun onBind(i:Intent?)=null
 override fun onDestroy(){player?.stop();player?.release();wakeLock?.let{if(it.isHeld)it.release()};getSystemService(Vibrator::class.java).cancel();super.onDestroy()}
 companion object{fun intent(c:Context)=Intent(c,AlarmService::class.java)}
}
