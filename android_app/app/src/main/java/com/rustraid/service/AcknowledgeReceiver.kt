package com.rustraid.service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.rustraid.data.FirebaseRepository
class AcknowledgeReceiver:BroadcastReceiver(){override fun onReceive(context:Context,intent:Intent){val laptopId=intent.getStringExtra(AlarmService.EXTRA_LAPTOP_ID)?:return;FirebaseRepository(laptopId).acknowledge();context.stopService(AlarmService.intent(context,laptopId=laptopId))}}
