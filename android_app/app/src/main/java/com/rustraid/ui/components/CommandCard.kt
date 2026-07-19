package com.rustraid.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp

@Composable
fun CommandCard(title: String, accent: Color = MaterialTheme.colorScheme.primary, modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    val alpha by rememberInfiniteTransition(label="glow").animateFloat(.45f,.95f,infiniteRepeatable(tween(1700),RepeatMode.Reverse),label="glowAlpha")
    Card(modifier=modifier,colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.surface),border=BorderStroke(1.dp,accent.copy(alpha=alpha)),elevation=CardDefaults.cardElevation(defaultElevation=5.dp)) {
        Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(10.dp)) {
            Text("// $title",color=accent,style=MaterialTheme.typography.labelLarge)
            content()
        }
    }
}
