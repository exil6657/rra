package com.rustraid.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.rustraid.ui.theme.*

@Composable fun AlertModeCard(title:String,detail:String,selected:Boolean,onClick:()->Unit,modifier:Modifier=Modifier){
    val accent=if(title.contains("PANIC")) Red else Purple
    Card(onClick=onClick,modifier=modifier,border=BorderStroke(if(selected)2.dp else 1.dp,if(selected)accent else Border),colors=CardDefaults.cardColors(containerColor=if(selected)accent.copy(alpha=.18f) else Field)){
        Column(Modifier.padding(12.dp),verticalArrangement=Arrangement.spacedBy(5.dp)){Text(title,color=if(selected)accent else TextPrimary,style=MaterialTheme.typography.labelLarge);Text(detail,color=Muted,style=MaterialTheme.typography.labelSmall);if(selected)Text("ACTIVE",color=accent,style=MaterialTheme.typography.labelSmall)}
    }
}
