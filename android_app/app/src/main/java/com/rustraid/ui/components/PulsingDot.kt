package com.rustraid.ui.components
import androidx.compose.animation.core.*;import androidx.compose.foundation.Canvas;import androidx.compose.runtime.*;import androidx.compose.ui.Modifier;import androidx.compose.ui.graphics.Color
@Composable fun PulsingDot(color:Color,modifier:Modifier=Modifier){val t=rememberInfiniteTransition(label="pulse").animateFloat(.35f,1f,infiniteRepeatable(tween(900),RepeatMode.Reverse),label="a");Canvas(modifier){drawCircle(color.copy(alpha=t.value),size.minDimension/2)}}
