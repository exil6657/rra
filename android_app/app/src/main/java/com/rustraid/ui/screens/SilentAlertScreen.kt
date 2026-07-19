package com.rustraid.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.rustraid.ui.components.CommandCard
import com.rustraid.ui.components.TypewriterText
import com.rustraid.ui.theme.*

@Composable fun SilentAlertScreen(onAcknowledge:()->Unit){Column(Modifier.fillMaxSize().background(Black).padding(24.dp),horizontalAlignment=Alignment.CenterHorizontally,verticalArrangement=Arrangement.Center){Text("RUST RAID",style=MaterialTheme.typography.headlineLarge);TypewriterText("// SILENT PROFILE ACTIVE",color=PurpleSoft);Spacer(Modifier.height(20.dp));CommandCard("RAID ALERT",Orange,Modifier.fillMaxWidth()){Text("A linked PC detected a raid. Review when ready, then acknowledge.",color=TextPrimary)};Spacer(Modifier.height(20.dp));Button(onClick=onAcknowledge,modifier=Modifier.fillMaxWidth()){Text("ACKNOWLEDGE",style=MaterialTheme.typography.labelLarge)}}
