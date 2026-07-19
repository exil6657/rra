package com.rustraid.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.rustraid.model.AlertSnapshot
import com.rustraid.model.AlertState
import com.rustraid.ui.components.AlertModeCard
@Composable fun DashboardScreen(snapshot:AlertSnapshot,onMode:(String)->Unit,onTest:()->Unit){
 var critical by remember{mutableStateOf(true)}
 val (headline,color,detail)=when(snapshot.state){AlertState.RAID_ACTIVE->Triple("🚨 RAID ACTIVE",Color(0xFFFF2D2D),"Acknowledge from the alarm screen");AlertState.COOLDOWN->Triple("⏱ COOLDOWN ACTIVE",Color(0xFFFF8C00),"Alerts are temporarily suppressed");AlertState.MONITORING->Triple("● MONITORING",Color(0xFF00FF88),"Watching synchronized alert state");else->Triple("⚠ DISCONNECTED",Color(0xFFA0A0A0),"Check Firebase configuration")}
 Column(Modifier.padding(20.dp),verticalArrangement=Arrangement.spacedBy(16.dp)){Card{Column(Modifier.padding(18.dp)){Text(headline,style=MaterialTheme.typography.headlineSmall,color=color);Text(detail);if(snapshot.message.isNotBlank())Text(snapshot.message)}};Text("Alert mode",style=MaterialTheme.typography.titleLarge);Row(horizontalArrangement=Arrangement.spacedBy(10.dp)){AlertModeCard("🔴 FULL PANIC","Alarm + flash + vibrate",critical,{critical=true;onMode("critical")},Modifier.weight(1f));AlertModeCard("🔵 SILENT ALERT","Notification + vibrate",!critical,{critical=false;onMode("silent")},Modifier.weight(1f))};Button(onClick=onTest,colors=ButtonDefaults.buttonColors(containerColor=MaterialTheme.colorScheme.error)){Text("🔴 Test synchronized alarm")};Text("Recent activity",style=MaterialTheme.typography.titleMedium);Text("Live state is synchronized through Firebase.")}
}
