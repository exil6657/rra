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
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.ContextCompat.startForegroundService
import androidx.compose.material3.*
import androidx.compose.runtime.*
import com.rustraid.service.AlarmService
import com.rustraid.service.FirebaseMonitorService
import com.rustraid.ui.screens.*
import com.rustraid.ui.theme.RustRaidTheme
class MainActivity:ComponentActivity(){
 override fun onCreate(b:Bundle?){super.onCreate(b);if(Build.VERSION.SDK_INT>=33&&ContextCompat.checkSelfPermission(this,Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED)ActivityCompat.requestPermissions(this,arrayOf(Manifest.permission.POST_NOTIFICATIONS),10);startForegroundService(this,Intent(this,FirebaseMonitorService::class.java));setContent{RustRaidTheme{var tab by remember{mutableIntStateOf(0)};Scaffold(bottomBar={NavigationBar{listOf("Dashboard","Log","Settings").forEachIndexed{i,n->NavigationBarItem(selected=tab==i,onClick={tab=i},icon={},label={Text(n)})}}}){p->Surface(modifier=androidx.compose.ui.Modifier.padding(p)){when(tab){0->DashboardScreen{startForegroundService(this,AlarmService.intent(this))};1->LogScreen();else->SettingsScreen(onBatteryExemption={requestBatteryExemption()})}}}}}
 }
 private fun requestBatteryExemption(){if(Build.VERSION.SDK_INT>=23)startActivity(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:$packageName")))}
}
