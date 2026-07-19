package com.rustraid
import android.app.Application
import android.content.Intent
import androidx.core.content.ContextCompat
import com.rustraid.data.FirebaseSession
import com.rustraid.service.FirebaseMonitorService
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.database.FirebaseDatabase
class RaidApplication:Application(){override fun onCreate(){super.onCreate();FirebaseSession.ensureAuthenticated({FirebaseMessaging.getInstance().token.addOnSuccessListener{token->FirebaseDatabase.getInstance().getReference("app_meta/phone_fcm_token").setValue(token)};ContextCompat.startForegroundService(this,Intent(this,FirebaseMonitorService::class.java))}){}}
