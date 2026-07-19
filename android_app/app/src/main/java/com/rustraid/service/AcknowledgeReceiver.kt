package com.rustraid.service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.rustraid.data.FirebaseRepository
class AcknowledgeReceiver:BroadcastReceiver(){override fun onReceive(context:Context,intent:Intent){FirebaseRepository().acknowledge();context.stopService(AlarmService.intent(context))}}
