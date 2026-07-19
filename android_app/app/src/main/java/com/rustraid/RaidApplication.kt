package com.rustraid
import android.app.Application
import android.content.Intent
import androidx.core.content.ContextCompat
import com.google.firebase.messaging.FirebaseMessaging
import com.rustraid.data.FirebaseSession
import com.rustraid.data.PairingManager
import com.rustraid.service.FirebaseMonitorService
class RaidApplication:Application(){override fun onCreate(){super.onCreate();FirebaseSession.ensureAuthenticated({FirebaseMessaging.getInstance().token.addOnSuccessListener{token->PairingManager(this).refreshFcmToken(token)};ContextCompat.startForegroundService(this,Intent(this,FirebaseMonitorService::class.java))}){}}}
