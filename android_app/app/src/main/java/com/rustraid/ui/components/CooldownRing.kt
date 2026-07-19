package com.rustraid.ui.components
import androidx.compose.foundation.Canvas;import androidx.compose.runtime.Composable;import androidx.compose.ui.Modifier;import androidx.compose.ui.graphics.Color
@Composable fun CooldownRing(progress:Float,modifier:Modifier=Modifier){Canvas(modifier){drawArc(Color(0xFFFF8C00),-90f,360*progress,false,style=androidx.compose.ui.graphics.drawscope.Stroke(10f))}}
