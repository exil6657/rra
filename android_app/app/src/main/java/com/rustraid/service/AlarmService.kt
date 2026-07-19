package com.rustraid.service
import android.app.*
import android.content.*
import android.media.*
import android.os.*
import androidx.core.app.NotificationCompat
import com.rustraid.AlarmActivity
import com.rustraid.R
class AlarmService:Service(){
 private var player:MediaPlayer?=null; private var wakeLock:PowerManager.WakeLock?=null; private var active=false
 override fun onStartCommand(i:Intent?,f:Int,id:Int):Int{
  if(active) return START_NOT_STICKY
  active=true
  val silent=i?.getBooleanExtra(EXTRA_SILENT,false)?:false;val manager=getSystemService(NotificationManager::class.java)
  manager.createNotificationChannel(NotificationChannel("raid","Wake alarms",NotificationManager.IMPORTANCE_HIGH));manager.createNotificationChannel(NotificationChannel("silent","Silent raid alerts",NotificationManager.IMPORTANCE_HIGH))
  val alarmIntent=PendingIntent.getActivity(this,1,Intent(this,AlarmActivity::class.java).putExtra(EXTRA_SILENT,silent).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
  val ackIntent=PendingIntent.getBroadcast(this,2,Intent(this,AcknowledgeReceiver::class.java),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
  val notice=NotificationCompat.Builder(this,if(silent) "silent" else "raid").setSmallIcon(android.R.drawable.ic_dialog_alert).setContentTitle(if(silent) "Raid alert" else "RAID ACTIVE — WAKE UP").setContentText(if(silent) "Tap to acknowledge" else "Alarm active; hold to acknowledge").setPriority(NotificationCompat.PRIORITY_MAX).setCategory(if(silent) NotificationCompat.CATEGORY_MESSAGE else NotificationCompat.CATEGORY_ALARM).setContentIntent(alarmIntent).addAction(0,"Acknowledge",ackIntent).apply{if(!silent)setFullScreenIntent(alarmIntent,true)}.build();startForeground(4,notice)
  if(!silent){val power=getSystemService(PowerManager::class.java);wakeLock=power.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"RustRaid:wakeAlarm").apply{acquire(10*60*1000L)};val audio=getSystemService(AudioManager::class.java);audio.setStreamVolume(AudioManager.STREAM_ALARM,audio.getStreamMaxVolume(AudioManager.STREAM_ALARM),0);player=MediaPlayer.create(this,R.raw.alarm_defcon).apply{isLooping=true;setAudioStreamType(AudioManager.STREAM_ALARM);start()};getSystemService(Vibrator::class.java).vibrate(VibrationEffect.createWaveform(longArrayOf(0,600,120,600,120,900),0))}
  return START_NOT_STICKY
 }
 override fun onBind(i:Intent?)=null
 override fun onDestroy(){active=false;player?.stop();player?.release();wakeLock?.let{if(it.isHeld)it.release()};getSystemService(Vibrator::class.java).cancel();super.onDestroy()}
 companion object{const val EXTRA_SILENT="silent";fun intent(c:Context,silent:Boolean=false)=Intent(c,AlarmService::class.java).putExtra(EXTRA_SILENT,silent)}
}
