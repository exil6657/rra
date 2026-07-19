package com.rustraid.service
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
class FCMReceiver:FirebaseMessagingService(){override fun onMessageReceived(message:RemoteMessage){startService(AlarmService.intent(this))}}
