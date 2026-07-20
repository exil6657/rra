package com.rustraid.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.rustraid.model.ActivityEntry
import com.rustraid.ui.components.CommandCard
import com.rustraid.ui.components.TypewriterText
import com.rustraid.ui.theme.*

@Composable fun LogScreen(entries:List<ActivityEntry>){
    var filter by remember{mutableStateOf("ALL")}
    val filtered=entries.filter{filter=="ALL"||when(filter){"RAIDS"->it.type=="raid";"ACK"->it.type=="acknowledged";"SYSTEM"->it.type in setOf("system","cooldown");else->true}}
    Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(18.dp)){
        Text("EVENT LOG",style=MaterialTheme.typography.headlineLarge);TypewriterText("// SYNCHRONIZED PC TELEMETRY",color=PurpleSoft);Spacer(Modifier.height(14.dp))
        Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){listOf("ALL","RAIDS","ACK","SYSTEM").forEach{label->FilterChip(selected=filter==label,onClick={filter=label},label={Text(label,style=MaterialTheme.typography.labelLarge)},colors=FilterChipDefaults.filterChipColors(selectedContainerColor=PurpleDeep,selectedLabelColor=TextPrimary))}}
        Spacer(Modifier.height(12.dp))
        if(filtered.isEmpty())CommandCard("NO EVENTS",Purple,Modifier.fillMaxWidth()){Text("NO MATCHING SYNCHRONIZED ACTIVITY",color=Muted)} else LazyColumn(verticalArrangement=Arrangement.spacedBy(9.dp)){items(filtered,key={it.id}){entry->val color=when(entry.type){"raid"->Red;"acknowledged"->Green;"cooldown"->Orange;"error"->Muted;else->Purple};CommandCard(entry.type.uppercase(),color,Modifier.fillMaxWidth()){Text(entry.timestamp,color=Muted,style=MaterialTheme.typography.labelSmall);Text(entry.description,color=TextPrimary,style=MaterialTheme.typography.bodyMedium)}}}
    }
}
