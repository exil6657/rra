package com.rustraid.ui.components
import androidx.compose.foundation.Canvas
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
@Composable fun CooldownRing(progress:Float,modifier:Modifier=Modifier){Canvas(modifier){drawArc(Color(0xFF2A2A2A),-90f,360f,false,style=Stroke(10f));drawArc(Color(0xFFFF8C00),-90f,360f*progress.coerceIn(0f,1f),false,style=Stroke(10f))}}
