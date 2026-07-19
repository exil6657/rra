package com.rustraid.service
import androidx.core.content.ContextCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.rustraid.data.PairingManager
class FCMReceiver:FirebaseMessagingService(){
 override fun onNewToken(token:String){PairingManager(applicationContext).refreshFcmToken(token)}
 override fun onMessageReceived(message:RemoteMessage){if(message.data["event"]=="raid_alarm"){val silent=message.data["mode"]=="silent";val vibration=message.data["vibration"]?.toBooleanStrictOrNull()?:true;val flash=message.data["flash"]?.toBooleanStrictOrNull()?:true;ContextCompat.startForegroundService(this,AlarmService.intent(this,silent,vibration,flash,message.data["laptop_id"]?:"",message.data["auto_silence_minutes"]?.toIntOrNull()?:5))}}
}
