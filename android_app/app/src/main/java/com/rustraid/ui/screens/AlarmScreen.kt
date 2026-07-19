package com.rustraid.ui.screens
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
@Composable fun AlarmScreen(flashEnabled:Boolean,onAcknowledge:()->Unit){
 var held by remember{mutableStateOf(false)};val transition=rememberInfiniteTransition(label="alarm");val scale by transition.animateFloat(.9f,1.1f,infiniteRepeatable(tween(400),RepeatMode.Reverse),label="s");val background by transition.animateColor(Color(0xFFFF0000),if(flashEnabled) Color(0xFF000000) else Color(0xFFFF0000),infiniteRepeatable(tween(250),RepeatMode.Reverse),label="flash")
 LaunchedEffect(held){if(held){kotlinx.coroutines.delay(1500);onAcknowledge()}}
 Column(Modifier.fillMaxSize().background(background).padding(24.dp),horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center){Text("🚨",fontSize=(100*scale).sp);Text("YOU ARE BEING RAIDED",fontSize=30.sp);Text("Get up NOW");Spacer(Modifier.height(48.dp));Button(onClick={},modifier=Modifier.pointerInput(Unit){detectTapGestures(onPress={held=true;tryAwaitRelease();held=false})}){Text(if(held)"KEEP HOLDING…" else "HOLD TO ACKNOWLEDGE")}}
}
