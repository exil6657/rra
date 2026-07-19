package com.rustraid.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
@Composable fun SilentAlertScreen(onAcknowledge:()->Unit){Column(Modifier.fillMaxSize().padding(28.dp),horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center){Text("Raid alert",style=MaterialTheme.typography.headlineLarge);Spacer(Modifier.height(12.dp));Text("Silent mode is active. Review and acknowledge when ready.");Spacer(Modifier.height(28.dp));Button(onClick=onAcknowledge){Text("Acknowledge")}}}
