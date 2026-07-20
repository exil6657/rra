package com.rustraid.ui.screens

import androidx.compose.animation.animateColor
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.rustraid.ui.components.TypewriterText
import com.rustraid.ui.theme.Red
import com.rustraid.ui.theme.TextPrimary

@Composable fun AlarmScreen(flashEnabled:Boolean,onAcknowledge:()->Unit){
    var held by remember{mutableStateOf(false)}
    val transition=rememberInfiniteTransition(label="alarm")
    val scale by transition.animateFloat(.88f,1.13f,infiniteRepeatable(tween(360),RepeatMode.Reverse),label="sirenScale")
    val background by transition.animateColor(Red,if(flashEnabled)Color.Black else Red,infiniteRepeatable(tween(240),RepeatMode.Reverse),label="flash")
    LaunchedEffect(held){if(held){kotlinx.coroutines.delay(1500);onAcknowledge()}}
    Column(Modifier.fillMaxSize().background(background).padding(28.dp),horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center){
        Text("⚠",fontSize=(106*scale).sp,color=TextPrimary)
        Text("RAID DETECTED",fontSize=34.sp,color=TextPrimary,style=MaterialTheme.typography.headlineLarge)
        Spacer(Modifier.height(8.dp));TypewriterText("// WAKE UP // ACKNOWLEDGE",color=TextPrimary,style=MaterialTheme.typography.labelLarge,speedMs=12)
        Spacer(Modifier.height(54.dp))
        Button(onClick={},modifier=Modifier.fillMaxWidth().height(76.dp).pointerInput(Unit){detectTapGestures(onPress={held=true;tryAwaitRelease();held=false})},colors=ButtonDefaults.buttonColors(containerColor=Color(0xFF00D884),contentColor=Color.Black)){Text(if(held)"HOLDING..." else "HOLD TO ACKNOWLEDGE",style=MaterialTheme.typography.labelLarge)}
    }
}
