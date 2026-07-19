package com.rustraid.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
@Composable fun PairingScreen(pending:Boolean,status:String,onPair:(String,String)->Unit){var code by remember{mutableStateOf("")};var name by remember{mutableStateOf("Android phone")};Column(Modifier.fillMaxSize().padding(24.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){Text("Link this phone",style=MaterialTheme.typography.headlineMedium);Text(if(pending)"Pairing request sent. Keep this app open until the laptop accepts it." else "Enter the pairing code displayed by your Rust Raid Alarm laptop app.");OutlinedTextField(value=code,onValueChange={code=it},label={Text("Pairing code")},singleLine=true,enabled=!pending);OutlinedTextField(value=name,onValueChange={name=it},label={Text("Phone name")},singleLine=true,enabled=!pending);Button(enabled=!pending&&code.isNotBlank(),onClick={onPair(code,name)}){Text("Request link")};if(status.isNotBlank())Text(status,color=MaterialTheme.colorScheme.primary);Text("The pairing code is only used to link this phone to one laptop.",style=MaterialTheme.typography.bodySmall)}}
