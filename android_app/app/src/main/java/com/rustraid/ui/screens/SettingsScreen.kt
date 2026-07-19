package com.rustraid.ui.screens
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import com.rustraid.model.AppSettings
@Composable fun SettingsScreen(settings:AppSettings,onUpdate:(Map<String,Any>)->Unit,onBatteryExemption:()->Unit,onFullScreenPermission:()->Unit,onUnlink:()->Unit,unlinkStatus:String){
 var quietStart by remember(settings.quietHoursStart){mutableStateOf(settings.quietHoursStart)};var quietEnd by remember(settings.quietHoursEnd){mutableStateOf(settings.quietHoursEnd)};var quietError by remember{mutableStateOf("")};var silence by remember(settings.autoSilenceMinutes){mutableFloatStateOf(settings.autoSilenceMinutes.toFloat())}
 Column(Modifier.padding(20.dp).verticalScroll(rememberScrollState()),verticalArrangement=Arrangement.spacedBy(14.dp)){
  Text("Settings",style=MaterialTheme.typography.headlineMedium)
  Text("Alarm target",style=MaterialTheme.typography.titleMedium);Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){TargetChip("Laptop","laptop",settings.deviceTarget,onUpdate);TargetChip("Phone","phone",settings.deviceTarget,onUpdate);TargetChip("Both","both",settings.deviceTarget,onUpdate)}
  Text("Phone alert mode",style=MaterialTheme.typography.titleMedium);Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){FilterChip(selected=settings.alertMode=="critical",onClick={onUpdate(mapOf("alert_mode" to "critical"))},label={Text("Full panic")});FilterChip(selected=settings.alertMode=="silent",onClick={onUpdate(mapOf("alert_mode" to "silent"))},label={Text("Silent")})}
  Text("Cooldown",style=MaterialTheme.typography.titleMedium);Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){listOf(30,60,120,240).forEach{minutes->FilterChip(selected=settings.cooldownMinutes==minutes,onClick={onUpdate(mapOf("cooldown_duration_minutes" to minutes))},label={Text("${if(minutes<60) "${minutes}m" else "${minutes/60}h"}")})}}
  Text("Auto-silence: ${silence.toInt()} minutes");Slider(value=silence,onValueChange={silence=it},onValueChangeFinished={onUpdate(mapOf("auto_silence_minutes" to silence.toInt()))},valueRange=1f..15f,steps=13)
  SettingSwitch("Screen flash",settings.screenFlash){onUpdate(mapOf("screen_flash" to it))};SettingSwitch("Vibration",settings.vibration){onUpdate(mapOf("vibration" to it))};SettingSwitch("Force maximum alarm volume",settings.volumeOverride){onUpdate(mapOf("volume_override" to it))};SettingSwitch("Quiet hours",settings.quietHoursEnabled){onUpdate(mapOf("quiet_hours_enabled" to it))}
  if(settings.quietHoursEnabled){Text("Quiet hours use 24-hour HH:MM format.");OutlinedTextField(value=quietStart,onValueChange={quietStart=it},label={Text("Start")},singleLine=true);OutlinedTextField(value=quietEnd,onValueChange={quietEnd=it},label={Text("End")},singleLine=true);Button(onClick={val formatter=DateTimeFormatter.ofPattern("HH:mm");val valid=runCatching{LocalTime.parse(quietStart,formatter);LocalTime.parse(quietEnd,formatter)}.isSuccess;if(valid){quietError="";onUpdate(mapOf("quiet_hours_start" to quietStart,"quiet_hours_end" to quietEnd))}else quietError="Use valid 24-hour times, for example 23:00 and 07:00."}){Text("Save quiet-hours schedule")};if(quietError.isNotBlank())Text(quietError,color=MaterialTheme.colorScheme.error)}
  SettingSwitch("AMOLED black theme",settings.amoledBlack){onUpdate(mapOf("amoled_black" to it))}
  Text("Connection",style=MaterialTheme.typography.titleMedium);Text("Settings are synchronized through Firebase.");Button(onClick=onBatteryExemption){Text("Exempt from battery saver")};Button(onClick=onFullScreenPermission){Text("Allow full-screen wake alarms")};OutlinedButton(onClick=onUnlink){Text("Unlink this phone")};if(unlinkStatus.isNotBlank())Text(unlinkStatus,color=MaterialTheme.colorScheme.error)
 }
}
@Composable private fun TargetChip(label:String,value:String,current:String,onUpdate:(Map<String,Any>)->Unit){FilterChip(selected=current==value,onClick={onUpdate(mapOf("device_target" to value))},label={Text(label)})}
@Composable private fun SettingSwitch(label:String,checked:Boolean,onChange:(Boolean)->Unit){Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){Text(label);Switch(checked=checked,onCheckedChange=onChange)}}
