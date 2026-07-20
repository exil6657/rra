package com.rustraid.service
import android.app.*
import android.content.*
import android.media.*
import android.net.Uri
import android.os.*
import androidx.core.app.NotificationCompat
import com.rustraid.AlarmActivity
import com.rustraid.R
import com.rustraid.data.FirebaseRepository
import com.rustraid.data.PreferencesManager
import kotlinx.coroutines.runBlocking
class AlarmService:Service(){
 private var player:MediaPlayer?=null;private var wakeLock:PowerManager.WakeLock?=null;private var active=false;private val handler=Handler(Looper.getMainLooper());private var laptopId="";private val autoStop=Runnable{if(laptopId.isNotBlank())FirebaseRepository(laptopId).acknowledge("phone-auto-silence");stopSelf()}
 override fun onStartCommand(i:Intent?,f:Int,id:Int):Int{
  if(active)return START_NOT_STICKY
  active=true;laptopId=i?.getStringExtra(EXTRA_LAPTOP_ID)?:"";val silent=i?.getBooleanExtra(EXTRA_SILENT,false)?:false;val vibration=i?.getBooleanExtra(EXTRA_VIBRATION,true)?:true;val flash=i?.getBooleanExtra(EXTRA_FLASH,true)?:true;val autoMinutes=(i?.getIntExtra(EXTRA_AUTO_SILENCE,5)?:5).coerceIn(1,15);val volumeOverride=i?.getBooleanExtra(EXTRA_VOLUME_OVERRIDE,true)?:true;val soundPreset=i?.getStringExtra(EXTRA_SOUND_PRESET)?:"defcon1";val manager=getSystemService(NotificationManager::class.java)
  manager.createNotificationChannel(NotificationChannel("raid","Wake alarms",NotificationManager.IMPORTANCE_HIGH));manager.createNotificationChannel(NotificationChannel("silent","Silent raid alerts",NotificationManager.IMPORTANCE_HIGH))
  val alarmIntent=PendingIntent.getActivity(this,1,Intent(this,AlarmActivity::class.java).putExtra(EXTRA_SILENT,silent).putExtra(EXTRA_FLASH,flash).putExtra(EXTRA_LAPTOP_ID,laptopId).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE);val ackIntent=PendingIntent.getBroadcast(this,2,Intent(this,AcknowledgeReceiver::class.java).putExtra(EXTRA_LAPTOP_ID,laptopId),PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
  val notice=NotificationCompat.Builder(this,if(silent)"silent" else "raid").setSmallIcon(android.R.drawable.ic_dialog_alert).setContentTitle(if(silent)"Raid alert" else "RAID ACTIVE — WAKE UP").setContentText(if(silent)"Tap to acknowledge" else "Alarm active; hold to acknowledge").setPriority(NotificationCompat.PRIORITY_MAX).setCategory(if(silent)NotificationCompat.CATEGORY_MESSAGE else NotificationCompat.CATEGORY_ALARM).setContentIntent(alarmIntent).addAction(0,"Acknowledge",ackIntent).apply{if(!silent)setFullScreenIntent(alarmIntent,true)}.build();startForeground(4,notice)
  if(!silent){val power=getSystemService(PowerManager::class.java);wakeLock=power.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK,"RustRaid:wakeAlarm").apply{acquire(10*60*1000L)};val audio=getSystemService(AudioManager::class.java);if(volumeOverride)audio.setStreamVolume(AudioManager.STREAM_ALARM,audio.getStreamMaxVolume(AudioManager.STREAM_ALARM),0);val sound=when(soundPreset){
    "tactical"->MediaPlayer.create(this,R.raw.alarm_tactical)
    "custom"->runCatching{val uri=runBlocking{PreferencesManager(this@AlarmService).getCustomSoundUri()};if(uri.isBlank())null else MediaPlayer.create(this,Uri.parse(uri))}.getOrNull()
    else->MediaPlayer.create(this,R.raw.alarm_defcon)
   }?:MediaPlayer.create(this,R.raw.alarm_defcon)
   player=sound.apply{isLooping=true;setAudioStreamType(AudioManager.STREAM_ALARM);start()};if(vibration)getSystemService(Vibrator::class.java).vibrate(VibrationEffect.createWaveform(longArrayOf(0,600,120,600,120,900),0))}
  handler.postDelayed(autoStop,autoMinutes*60_000L);return START_NOT_STICKY
 }
 override fun onBind(i:Intent?)=null
 override fun onDestroy(){active=false;handler.removeCallbacks(autoStop);player?.stop();player?.release();wakeLock?.let{if(it.isHeld)it.release()};getSystemService(Vibrator::class.java).cancel();super.onDestroy()}
 companion object{const val EXTRA_SILENT="silent";const val EXTRA_VIBRATION="vibration";const val EXTRA_FLASH="flash";const val EXTRA_LAPTOP_ID="laptop_id";const val EXTRA_AUTO_SILENCE="auto_silence_minutes";const val EXTRA_VOLUME_OVERRIDE="volume_override";const val EXTRA_SOUND_PRESET="sound_preset";fun intent(c:Context,silent:Boolean=false,vibration:Boolean=true,flash:Boolean=true,laptopId:String="",autoSilenceMinutes:Int=5,volumeOverride:Boolean=true,soundPreset:String="defcon1")=Intent(c,AlarmService::class.java).putExtra(EXTRA_SILENT,silent).putExtra(EXTRA_VIBRATION,vibration).putExtra(EXTRA_FLASH,flash).putExtra(EXTRA_LAPTOP_ID,laptopId).putExtra(EXTRA_AUTO_SILENCE,autoSilenceMinutes).putExtra(EXTRA_VOLUME_OVERRIDE,volumeOverride).putExtra(EXTRA_SOUND_PRESET,soundPreset)}
}
