package com.rustraid
import android.app.Application;import android.content.Intent;import com.rustraid.service.FirebaseMonitorService
class RaidApplication:Application(){override fun onCreate(){super.onCreate();startService(Intent(this,FirebaseMonitorService::class.java))}}
