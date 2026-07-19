package com.rustraid.service
import androidx.core.content.ContextCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.rustraid.data.FirebaseSession
import com.google.firebase.database.FirebaseDatabase
class FCMReceiver:FirebaseMessagingService(){
 override fun onNewToken(token:String){
  FirebaseSession.ensureAuthenticated({FirebaseDatabase.getInstance().getReference("app_meta/phone_fcm_token").setValue(token)},{})
 }
 override fun onMessageReceived(message:RemoteMessage){
  if(message.data["event"]=="raid_alarm") ContextCompat.startForegroundService(this,AlarmService.intent(this,message.data["mode"]=="silent"))
 }
}
