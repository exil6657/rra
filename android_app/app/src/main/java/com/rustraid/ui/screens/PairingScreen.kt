package com.rustraid.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun PairingScreen(pending: Boolean, status: String, onPair: (String, String) -> Unit, onCancel: () -> Unit) {
    var code by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("Android phone") }
    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        Text("Link this phone", style = MaterialTheme.typography.headlineMedium)
        Text(if (pending) "Pairing request sent. Keep this app open until the laptop accepts it." else "Enter the full pairing code shown by the laptop.")
        OutlinedTextField(value = code, onValueChange = { code = it }, label = { Text("Pairing code") }, singleLine = true, enabled = !pending)
        OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Phone name") }, singleLine = true, enabled = !pending)
        Button(enabled = !pending && code.isNotBlank(), onClick = { onPair(code, name) }) { Text("Request link") }
        if (pending) OutlinedButton(onClick = onCancel) { Text("Cancel pairing request") }
        if (status.isNotBlank()) Text(status, color = MaterialTheme.colorScheme.primary)
        Text("The laptop displays a QR version of this code for convenience. Copy or type the full code here to link this phone. Pairing requests expire after ten minutes.", style = MaterialTheme.typography.bodySmall)
    }
}
