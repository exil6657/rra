package com.rustraid.ui.screens

import android.content.Intent
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.rustraid.model.AppSettings
import com.rustraid.ui.components.CommandCard
import com.rustraid.ui.components.TypewriterText
import com.rustraid.ui.theme.*
import java.time.LocalTime
import java.time.format.DateTimeFormatter

@Composable
fun SettingsScreen(settings:AppSettings,onUpdate:(Map<String,Any>)->Unit,onBatteryExemption:()->Unit,onFullScreenPermission:()->Unit,onDndAccess:()->Unit,onNotifications:()->Unit,onUnlink:()->Unit,unlinkStatus:String,customSoundUri:String,onCustomSound:(String)->Unit){
    val context=LocalContext.current
    val customPicker=rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()){uri->if(uri!=null){runCatching{context.contentResolver.takePersistableUriPermission(uri,Intent.FLAG_GRANT_READ_URI_PERMISSION)};onCustomSound(uri.toString());onUpdate(mapOf("phone_sound_preset" to "custom"))}}
    var quietStart by remember(settings.quietHoursStart){mutableStateOf(settings.quietHoursStart)}
    var quietEnd by remember(settings.quietHoursEnd){mutableStateOf(settings.quietHoursEnd)}
    var quietError by remember{mutableStateOf("")}
    var silence by remember(settings.autoSilenceMinutes){mutableFloatStateOf(settings.autoSilenceMinutes.toFloat())}
    Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).verticalScroll(rememberScrollState()).padding(18.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
        Text("CONFIGURATION",style=MaterialTheme.typography.headlineLarge)
        TypewriterText("// THIS PHONE PROFILE",color=PurpleSoft)
        CommandCard("PROFILE MODE",Purple,Modifier.fillMaxWidth()){
            Text("These controls apply only to this phone. The PC controls which linked phones are enabled.",color=Muted,style=MaterialTheme.typography.bodyMedium)
            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){ProfileChip("FULL PANIC",settings.alertMode=="critical"){onUpdate(mapOf("alert_mode" to "critical"))};ProfileChip("SILENT",settings.alertMode=="silent"){onUpdate(mapOf("alert_mode" to "silent"))}}
        }
        CommandCard("ALARM ENGINE",Red,Modifier.fillMaxWidth()){
            Text("PHONE ALARM SOUND",style=MaterialTheme.typography.labelLarge,color=PurpleSoft)
            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){ProfileChip("DEFCON",settings.phoneSoundPreset=="defcon1"){onUpdate(mapOf("phone_sound_preset" to "defcon1"))};ProfileChip("TACTICAL",settings.phoneSoundPreset=="tactical"){onUpdate(mapOf("phone_sound_preset" to "tactical"))};ProfileChip("CUSTOM",settings.phoneSoundPreset=="custom"){onUpdate(mapOf("phone_sound_preset" to "custom"))}}
            if(settings.phoneSoundPreset=="custom"){OutlinedButton(onClick={customPicker.launch(arrayOf("audio/*"))},modifier=Modifier.fillMaxWidth()){Text("SELECT CUSTOM AUDIO")};Text(if(customSoundUri.isBlank())"NO FILE SELECTED // DEFCON FALLBACK" else "CUSTOM FILE READY",color=if(customSoundUri.isBlank())Orange else Green,style=MaterialTheme.typography.labelLarge)}
            ProfileSwitch("Vibration",settings.vibration){onUpdate(mapOf("vibration" to it))};ProfileSwitch("Screen flash",settings.screenFlash){onUpdate(mapOf("screen_flash" to it))};ProfileSwitch("Force maximum alarm volume",settings.volumeOverride){onUpdate(mapOf("volume_override" to it))}
        }
        CommandCard("COOLDOWN PROTOCOL",Orange,Modifier.fillMaxWidth()){
            Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){listOf(30,60,120,240).forEach{minutes->ProfileChip(if(minutes<60)"${minutes}M" else "${minutes/60}H",settings.cooldownMinutes==minutes){onUpdate(mapOf("cooldown_duration_minutes" to minutes))}}}
            Text("AUTO-SILENCE // ${silence.toInt()} MINUTES",style=MaterialTheme.typography.labelLarge,color=PurpleSoft)
            Slider(value=silence,onValueChange={silence=it},onValueChangeFinished={onUpdate(mapOf("auto_silence_minutes" to silence.toInt()))},valueRange=1f..15f,steps=13)
            ProfileSwitch("Quiet hours",settings.quietHoursEnabled){onUpdate(mapOf("quiet_hours_enabled" to it))}
            if(settings.quietHoursEnabled){OutlinedTextField(value=quietStart,onValueChange={quietStart=it},label={Text("QUIET START // HH:MM")},singleLine=true,modifier=Modifier.fillMaxWidth());OutlinedTextField(value=quietEnd,onValueChange={quietEnd=it},label={Text("QUIET END // HH:MM")},singleLine=true,modifier=Modifier.fillMaxWidth());Button(onClick={val formatter=DateTimeFormatter.ofPattern("HH:mm");val valid=runCatching{LocalTime.parse(quietStart,formatter);LocalTime.parse(quietEnd,formatter)}.isSuccess;if(valid){quietError="";onUpdate(mapOf("quiet_hours_start" to quietStart,"quiet_hours_end" to quietEnd))}else quietError="USE 24-HOUR HH:MM TIMES"},modifier=Modifier.fillMaxWidth()){Text("SAVE QUIET SCHEDULE")};if(quietError.isNotBlank())Text(quietError,color=Red,style=MaterialTheme.typography.labelLarge)}
            ProfileSwitch("Keep screen on during cooldown",settings.keepScreenOnDuringCooldown){onUpdate(mapOf("keep_screen_on_during_cooldown" to it))}
        }
        CommandCard("DEVICE ACCESS",Purple,Modifier.fillMaxWidth()){
            ProfileSwitch("AMOLED black theme",settings.amoledBlack){onUpdate(mapOf("amoled_black" to it))}
            OutlinedButton(onClick=onNotifications,modifier=Modifier.fillMaxWidth()){Text("ALLOW NOTIFICATIONS")};OutlinedButton(onClick=onBatteryExemption,modifier=Modifier.fillMaxWidth()){Text("EXEMPT FROM BATTERY SAVER")};OutlinedButton(onClick=onFullScreenPermission,modifier=Modifier.fillMaxWidth()){Text("ALLOW FULL-SCREEN WAKE ALARMS")};OutlinedButton(onClick=onDndAccess,modifier=Modifier.fillMaxWidth()){Text("ALLOW DND ALARM ACCESS")}
        }
        CommandCard("PAIRING CONTROL",Red,Modifier.fillMaxWidth()){
            OutlinedButton(onClick=onUnlink,modifier=Modifier.fillMaxWidth(),colors=ButtonDefaults.outlinedButtonColors(contentColor=Red)){Text("UNLINK THIS PHONE")};if(unlinkStatus.isNotBlank())Text(unlinkStatus,color=Red,style=MaterialTheme.typography.labelLarge)
        }
        Spacer(Modifier.height(18.dp))
    }
}
@Composable private fun ProfileChip(label:String,selected:Boolean,onClick:()->Unit){FilterChip(selected=selected,onClick=onClick,label={Text(label,style=MaterialTheme.typography.labelLarge)},colors=FilterChipDefaults.filterChipColors(selectedContainerColor=PurpleDeep,selectedLabelColor=TextPrimary))}
@Composable private fun ProfileSwitch(label:String,checked:Boolean,onChange:(Boolean)->Unit){Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.SpaceBetween){Text(label,style=MaterialTheme.typography.bodyMedium);Switch(checked=checked,onCheckedChange=onChange)}}
