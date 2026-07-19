package com.rustraid

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.compose.foundation.layout.padding
import androidx.compose.ui.Modifier
import androidx.activity.compose.setContent
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.ContextCompat.startForegroundService
import androidx.lifecycle.lifecycleScope
import com.google.firebase.database.ValueEventListener
import com.rustraid.data.*
import com.rustraid.model.*
import com.rustraid.service.FirebaseMonitorService
import com.rustraid.ui.screens.*
import com.rustraid.ui.theme.RustRaidTheme
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    private var alarmListener: ValueEventListener? = null
    private var activityListener: ValueEventListener? = null
    private var settingsListener: ValueEventListener? = null
    private var pairingListener: ValueEventListener? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 33 && ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 10)
        }
        FirebaseSession.ensureAuthenticated({}, {})
        setContent {
            val pairingManager = remember { PairingManager(applicationContext) }
            val pairing by pairingManager.info.collectAsState(initial = PairingInfo())
            if (pairing.linked) LinkedApp(pairing, pairingManager)
            else RustRaidTheme { PairingFlow(pairing, pairingManager) }
        }
    }

    @Composable
    private fun PairingFlow(pairing: PairingInfo, manager: PairingManager) {
        var message by remember { mutableStateOf("") }
        val repository = remember(pairing.laptopId) { FirebaseRepository(pairing.laptopId) }
        DisposableEffect(pairing.laptopId, pairing.phoneId, pairing.pendingSecret) {
            if (pairing.laptopId.isNotBlank() && pairing.pendingSecret.isNotBlank()) {
                pairingListener = repository.watchPairAcceptance(pairing.phoneId) {
                    lifecycleScope.launch {
                        manager.confirmLinked()
                        startForegroundService(this@MainActivity, Intent(this@MainActivity, FirebaseMonitorService::class.java))
                    }
                }
            }
            onDispose {
                pairingListener?.let(repository::removePairAcceptanceListener)
                pairingListener = null
            }
        }
        PairingScreen(
            pending = pairing.laptopId.isNotBlank() && pairing.pendingSecret.isNotBlank(),
            status = message,
            onPair = { code, name ->
                lifecycleScope.launch {
                    manager.request(code, name) { result ->
                        message = if (result.isSuccess) "Pair request sent. Accept it on the PC."
                        else result.exceptionOrNull()?.message ?: "Pairing failed."
                    }
                }
            },
            onCancel = {
                lifecycleScope.launch {
                    manager.cancelPending(pairing)
                    message = "Pairing request cancelled."
                }
            }
        )
    }

    @Composable
    private fun LinkedApp(pairing: PairingInfo, manager: PairingManager) {
        val firebase = remember(pairing.laptopId) { FirebaseRepository(pairing.laptopId) }
        val preferences = remember { PreferencesManager(applicationContext) }
        val customSoundUri by preferences.customSoundUri.collectAsState(initial = "")
        var unlinkStatus by remember { mutableStateOf("") }
        var tab by remember { mutableIntStateOf(0) }
        var snapshot by remember { mutableStateOf(AlertSnapshot(AlertState.DISCONNECTED)) }
        var entries by remember { mutableStateOf(emptyList<ActivityEntry>()) }
        var settings by remember { mutableStateOf(AppSettings()) }

        DisposableEffect(pairing.laptopId) {
            alarmListener = firebase.watchAlarm({ snapshot = it }, { snapshot = AlertSnapshot(AlertState.DISCONNECTED) })
            activityListener = firebase.watchActivity { entries = it }
            settingsListener = firebase.watchSettings { settings = it }
            firebase.heartbeat()
            onDispose {
                alarmListener?.let(firebase::removeAlarmListener)
                activityListener?.let(firebase::removeActivityListener)
                settingsListener?.let(firebase::removeSettingsListener)
                alarmListener = null
                activityListener = null
                settingsListener = null
            }
        }
        DisposableEffect(snapshot.state, settings.keepScreenOnDuringCooldown) {
            if (snapshot.state == AlertState.COOLDOWN && settings.keepScreenOnDuringCooldown) window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            else window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            onDispose { window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON) }
        }

        RustRaidTheme(amoledBlack = settings.amoledBlack) {
            Scaffold(bottomBar = {
                NavigationBar {
                    listOf("Dashboard", "Log", "Settings").forEachIndexed { index, name ->
                        NavigationBarItem(selected = tab == index, onClick = { tab = index }, icon = {}, label = { Text(name) })
                    }
                }
            }) { padding ->
                Surface(modifier = Modifier.padding(padding)) {
                    when (tab) {
                        0 -> DashboardScreen(snapshot, settings.cooldownMinutes, { firebase.setMode(it) }, { firebase.triggerLocalTest() })
                        1 -> LogScreen(entries)
                        else -> SettingsScreen(
                            settings,
                            { firebase.updateSettings(it) },
                            { requestBatteryExemption() },
                            { requestFullScreenPermission() },
                            { requestDndAccess() },
                            { requestNotificationPermission() },
                            {
                                lifecycleScope.launch {
                                    manager.requestUnlink(pairing) { result ->
                                        if (result.isSuccess) lifecycleScope.launch {
                                            manager.unlink()
                                            stopService(Intent(this@MainActivity, FirebaseMonitorService::class.java))
                                        } else unlinkStatus = result.exceptionOrNull()?.message ?: "Unlink request failed."
                                    }
                                }
                            },
                            unlinkStatus,
                            customSoundUri,
                            { uri -> lifecycleScope.launch { preferences.setCustomSoundUri(uri) } }
                        )
                    }
                }
            }
        }
    }

    private fun requestBatteryExemption() {
        if (Build.VERSION.SDK_INT >= 23) startActivity(Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:$packageName")))
    }
    private fun requestFullScreenPermission() {
        if (Build.VERSION.SDK_INT >= 34) startActivity(Intent(Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT, Uri.parse("package:$packageName")))
    }
    private fun requestDndAccess() { startActivity(Intent(Settings.ACTION_NOTIFICATION_POLICY_ACCESS_SETTINGS)) }
    private fun requestNotificationPermission() {
        if (Build.VERSION.SDK_INT >= 33) ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 10)
        else startActivity(Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(Settings.EXTRA_APP_PACKAGE, packageName))
    }
}
