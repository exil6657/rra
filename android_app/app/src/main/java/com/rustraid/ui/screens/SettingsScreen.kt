package com.rustraid.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.rustraid.model.AppSettings
@Composable fun SettingsScreen(settings:AppSettings,onUpdate:(Map<String,Any>)->Unit,onBatteryExemption:()->Unit){
 Column(Modifier.padding(20.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
  Text("Settings",style=MaterialTheme.typography.headlineMedium)
  Text("Alert mode",style=MaterialTheme.typography.titleMedium)
  Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){FilterChip(selected=settings.alertMode=="critical",onClick={onUpdate(mapOf("alert_mode" to "critical"))},label={Text("Full panic")});FilterChip(selected=settings.alertMode=="silent",onClick={onUpdate(mapOf("alert_mode" to "silent"))},label={Text("Silent")})}
  Text("Cooldown",style=MaterialTheme.typography.titleMedium)
  Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){listOf(30,60,120,240).forEach{minutes->FilterChip(selected=settings.cooldownMinutes==minutes,onClick={onUpdate(mapOf("cooldown_duration_minutes" to minutes))},label={Text("${if(minutes<60) "${minutes}m" else "${minutes/60}h"}")})}}
  SettingSwitch("Screen flash",settings.screenFlash){onUpdate(mapOf("screen_flash" to it))};SettingSwitch("Vibration",settings.vibration){onUpdate(mapOf("vibration" to it))};SettingSwitch("Quiet hours",settings.quietHoursEnabled){onUpdate(mapOf("quiet_hours_enabled" to it))};SettingSwitch("AMOLED black theme",settings.amoledBlack){onUpdate(mapOf("amoled_black" to it))}
  Text("Connection",style=MaterialTheme.typography.titleMedium);Text("Settings are synchronized through Firebase.");Button(onClick=onBatteryExemption){Text("Exempt from battery saver")}
 }
}
@Composable private fun SettingSwitch(label:String,checked:Boolean,onChange:(Boolean)->Unit){Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){Text(label);Switch(checked=checked,onCheckedChange=onChange)}}
