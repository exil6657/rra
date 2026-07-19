package com.rustraid
import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.ContextCompat.startForegroundService
import com.google.firebase.database.ValueEventListener
import com.rustraid.data.FirebaseRepository
import com.rustraid.data.FirebaseSession
import com.rustraid.model.AlertSnapshot
import com.rustraid.model.AlertState
import com.rustraid.model.ActivityEntry
import com.rustraid.model.AppSettings
import com.rustraid.service.FirebaseMonitorService
import com.rustraid.ui.screens.*
import com.rustraid.ui.theme.RustRaidTheme
class MainActivity:ComponentActivity(){
 private val firebase=FirebaseRepository(); private var listener:ValueEventListener?=null; private var activityListener:ValueEventListener?=null; private var settingsListener:ValueEventListener?=null
 override fun onCreate(b:Bundle?){super.onCreate(b);if(Build.VERSION.SDK_INT>=33&&ContextCompat.checkSelfPermission(this,Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)ActivityCompat.requestPermissions(this,arrayOf(Manifest.permission.POST_NOTIFICATIONS),10);FirebaseSession.ensureAuthenticated({startForegroundService(this,Intent(this,FirebaseMonitorService::class.java))},{});setContent{RustRaidTheme{var tab by remember{mutableIntStateOf(0)};var snapshot by remember{mutableStateOf(AlertSnapshot(AlertState.DISCONNECTED))};var entries by remember{mutableStateOf(emptyList<ActivityEntry>())};var settings by remember{mutableStateOf(AppSettings())};DisposableEffect(Unit){listener=firebase.watchAlarm({snapshot=it},{snapshot=AlertSnapshot(AlertState.DISCONNECTED)});activityListener=firebase.watchActivity{entries=it};settingsListener=firebase.watchSettings{settings=it};onDispose{listener?.let(firebase::removeAlarmListener);activityListener?.let(firebase::removeActivityListener);settingsListener?.let(firebase::removeSettingsListener);listener=null;activityListener=null;settingsListener=null}};Scaffold(bottomBar={NavigationBar{listOf("Dashboard","Log","Settings").forEachIndexed{i,n->NavigationBarItem(selected=tab==i,onClick={tab=i},icon={},label={Text(n)})}}}){p->Surface(modifier=androidx.compose.ui.Modifier.padding(p)){when(tab){0->DashboardScreen(snapshot,{firebase.setMode(it)},{firebase.triggerLocalTest()});1->LogScreen(entries);else->SettingsScreen(settings,{firebase.updateSettings(it)},{requestBatteryExemption()},{requestFullScreenPermission()})}}}}}}
 private fun requestBatteryExemption(){if(Build.VERSION.SDK_INT>=23)startActivity(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,Uri.parse("package:$packageName")))}
 private fun requestFullScreenPermission(){if(Build.VERSION.SDK_INT>=34)startActivity(Intent(Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT,Uri.parse("package:$packageName")))}
}
