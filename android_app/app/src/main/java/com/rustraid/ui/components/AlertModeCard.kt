package com.rustraid.ui.components
import androidx.compose.material3.*;import androidx.compose.runtime.Composable;import androidx.compose.ui.Modifier
@Composable fun AlertModeCard(title:String,detail:String,selected:Boolean,onClick:()->Unit,modifier:Modifier=Modifier){ElevatedCard(onClick=onClick,modifier=modifier){ListItem(headlineContent={Text(title)},supportingContent={Text(detail)},trailingContent=if(selected) ({ Text("✓") }) else null)}}
