package com.rustraid.ui.components

import androidx.compose.animation.core.*
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import kotlinx.coroutines.delay

@Composable
fun TypewriterText(text: String, color: Color = MaterialTheme.colorScheme.primary, style: TextStyle = MaterialTheme.typography.labelLarge, speedMs: Long = 16) {
    var visible by remember(text) { mutableIntStateOf(0) }
    val cursorAlpha by rememberInfiniteTransition(label="cursor").animateFloat(0f,1f,infiniteRepeatable(tween(480),RepeatMode.Reverse),label="cursorAlpha")
    LaunchedEffect(text) { visible=0; while(visible<text.length){ delay(speedMs); visible++ } }
    Text(text=text.take(visible)+(if(visible<text.length || cursorAlpha>.5f) "▋" else ""),color=color,style=style)
}
