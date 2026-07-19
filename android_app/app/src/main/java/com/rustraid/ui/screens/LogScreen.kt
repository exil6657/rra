package com.rustraid.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.rustraid.model.ActivityEntry
@Composable fun LogScreen(entries:List<ActivityEntry>){
 Column(Modifier.padding(20.dp)){Text("Activity log",style=MaterialTheme.typography.headlineMedium);Spacer(Modifier.height(12.dp));if(entries.isEmpty())Text("No synchronized activity recorded.") else LazyColumn(verticalArrangement=Arrangement.spacedBy(8.dp)){items(entries,key={it.id}){entry->val color=when{entry.description.contains("Alert",true)->Color(0xFFFF2D2D);entry.description.contains("Acknowledged",true)->Color(0xFF00FF88);entry.description.contains("Cooldown",true)->Color(0xFFFF8C00);entry.description.contains("error",true)->Color(0xFFA0A0A0);else->Color(0xFF00A8FF)};Card{Column(Modifier.padding(12.dp)){Text(entry.timestamp,color=Color(0xFFA0A0A0),style=MaterialTheme.typography.labelSmall);Text(entry.description,color=color)}}}}}
}
