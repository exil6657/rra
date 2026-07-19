package com.rustraid
import android.app.Application
import android.content.Intent
import androidx.core.content.ContextCompat
import com.rustraid.data.FirebaseSession
import com.rustraid.service.FirebaseMonitorService
class RaidApplication:Application(){override fun onCreate(){super.onCreate();FirebaseSession.ensureAuthenticated({ContextCompat.startForegroundService(this,Intent(this,FirebaseMonitorService::class.java))}){}}
