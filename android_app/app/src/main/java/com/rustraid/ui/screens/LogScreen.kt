package com.rustraid.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.rustraid.model.ActivityEntry
@Composable fun LogScreen(entries:List<ActivityEntry>){
 var filter by remember{mutableStateOf("All")};val filtered=entries.filter{filter=="All"||when(filter){"Raids"->it.type=="raid";"Acknowledged"->it.type=="acknowledged";"System"->it.type in setOf("system","cooldown");else->true}}
 Column(Modifier.padding(20.dp)){Text("Activity log",style=MaterialTheme.typography.headlineMedium);Spacer(Modifier.height(12.dp));Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){listOf("All","Raids","Acknowledged","System").forEach{label->FilterChip(selected=filter==label,onClick={filter=label},label={Text(label)})}};Spacer(Modifier.height(12.dp));if(filtered.isEmpty())Text("No matching synchronized activity.") else LazyColumn(verticalArrangement=Arrangement.spacedBy(8.dp)){items(filtered,key={it.id}){entry->val color=when(entry.type){"raid"->Color(0xFFFF2D2D);"acknowledged"->Color(0xFF00FF88);"cooldown"->Color(0xFFFF8C00);"error"->Color(0xFFA0A0A0);else->Color(0xFF00A8FF)};Card{Column(Modifier.padding(12.dp)){Text(entry.timestamp,color=Color(0xFFA0A0A0),style=MaterialTheme.typography.labelSmall);Text(entry.description,color=color)}}}}}
}
