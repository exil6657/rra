package com.rustraid.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.rustraid.model.AlertSnapshot
import com.rustraid.model.AlertState
import com.rustraid.ui.components.AlertModeCard
import com.rustraid.ui.components.CommandCard
import com.rustraid.ui.components.CooldownRing
import com.rustraid.ui.components.TypewriterText
import com.rustraid.ui.theme.*
import java.time.Instant

@Composable
fun DashboardScreen(snapshot:AlertSnapshot,cooldownMinutes:Int,onMode:(String)->Unit,onTest:()->Unit){
    var critical by remember { mutableStateOf(true) }
    var now by remember { mutableLongStateOf(System.currentTimeMillis()) }
    LaunchedEffect(snapshot.cooldownUntil,snapshot.state){ while(snapshot.state==AlertState.COOLDOWN){ now=System.currentTimeMillis();kotlinx.coroutines.delay(1000) } }
    val remaining=snapshot.cooldownUntil?.let { runCatching{(Instant.parse(it).toEpochMilli()-now).coerceAtLeast(0)}.getOrDefault(0) }?:0
    val cooldownText="${remaining/60_000}:${"%02d".format((remaining/1000)%60)}"
    val (headline,accent,detail)=when(snapshot.state){
        AlertState.RAID_ACTIVE->Triple("RAID ACTIVE",Red,"ACKNOWLEDGE IMMEDIATELY")
        AlertState.COOLDOWN->Triple("COOLDOWN",Orange,"$cooldownText REMAINING")
        AlertState.MONITORING->Triple("MONITORING",Green,"LINK ESTABLISHED")
        else->Triple("OFFLINE",Muted,"CHECK FIREBASE CONNECTION")
    }
    Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(18.dp),verticalArrangement=Arrangement.spacedBy(14.dp)) {
        Row(verticalAlignment=Alignment.CenterVertically,modifier=Modifier.fillMaxWidth()) {
            Column(Modifier.weight(1f)) { Text("RUST RAID",style=MaterialTheme.typography.headlineLarge);TypewriterText("// PC LINK COMMAND",color=PurpleSoft) }
            Surface(color=accent.copy(alpha=.13f),shape=MaterialTheme.shapes.large) { Text("● $headline",color=accent,style=MaterialTheme.typography.labelLarge,modifier=Modifier.padding(horizontal=10.dp,vertical=7.dp)) }
        }
        CommandCard("LIVE STATUS",accent,Modifier.fillMaxWidth()) {
            Row(verticalAlignment=Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) { Text(headline,style=MaterialTheme.typography.headlineMedium,color=accent);Text(detail,color=Muted,style=MaterialTheme.typography.labelLarge);if(snapshot.message.isNotBlank())Text(snapshot.message,style=MaterialTheme.typography.bodyMedium) }
                if(snapshot.state==AlertState.COOLDOWN) Box(contentAlignment=Alignment.Center){CooldownRing(remaining.toFloat()/(cooldownMinutes.coerceAtLeast(1)*60_000f),Modifier.size(68.dp));Text(cooldownText,style=MaterialTheme.typography.labelSmall)}
            }
        }
        CommandCard("ALERT MODE",Purple,Modifier.fillMaxWidth()) {
            Row(horizontalArrangement=Arrangement.spacedBy(10.dp)) {
                AlertModeCard("FULL PANIC","SOUND + FLASH",critical,{critical=true;onMode("critical")},Modifier.weight(1f))
                AlertModeCard("SILENT","NOTIFICATION ONLY",!critical,{critical=false;onMode("silent")},Modifier.weight(1f))
            }
        }
        CommandCard("SYSTEM ACTION",Red,Modifier.fillMaxWidth()) {
            Button(onClick=onTest,modifier=Modifier.fillMaxWidth(),colors=ButtonDefaults.buttonColors(containerColor=Red,contentColor=Color.White)) { Text("◉  INITIATE TEST RAID",style=MaterialTheme.typography.labelLarge) }
        }
        Spacer(Modifier.weight(1f))
        Text("ENCRYPTED PAIR LINK // LIVE FIREBASE STATE",color=Muted,style=MaterialTheme.typography.labelSmall)
    }
}
