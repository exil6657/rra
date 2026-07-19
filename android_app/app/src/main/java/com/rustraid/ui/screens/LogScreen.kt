package com.rustraid.ui.screens
import androidx.compose.foundation.layout.*;import androidx.compose.material3.*;import androidx.compose.runtime.Composable;import androidx.compose.ui.Modifier;import androidx.compose.ui.unit.dp
@Composable fun LogScreen(){Column(Modifier.padding(20.dp)){Text("Activity log",style=MaterialTheme.typography.headlineMedium);AssistChip(onClick={},label={Text("All")});Text("No activity recorded.",Modifier.padding(top=16.dp))}}
