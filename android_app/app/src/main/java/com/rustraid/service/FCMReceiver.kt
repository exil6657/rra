package com.rustraid.service
import androidx.core.content.ContextCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.rustraid.data.FirebaseSession
import com.google.firebase.database.FirebaseDatabase
class FCMReceiver:FirebaseMessagingService(){
 override fun onNewToken(token:String){FirebaseSession.ensureAuthenticated({FirebaseDatabase.getInstance().getReference("app_meta/phone_fcm_token").setValue(token)},{})}
 override fun onMessageReceived(message:RemoteMessage){
  if(message.data["event"]=="raid_alarm"){
   val silent=message.data["mode"]=="silent";val vibration=message.data["vibration"]?.toBooleanStrictOrNull()?:true;val flash=message.data["flash"]?.toBooleanStrictOrNull()?:true
   ContextCompat.startForegroundService(this,AlarmService.intent(this,silent,vibration,flash,message.data["laptop_id"]?:""))
  }
 }
}
