package com.rustraid.ui.screens

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions

@Composable
fun PairingScreen(pending: Boolean, status: String, onPair: (String, String) -> Unit, onCancel: () -> Unit) {
    var code by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("${Build.MANUFACTURER} ${Build.MODEL}".trim()) }
    var scannerMessage by remember { mutableStateOf("") }
    val scanner = rememberLauncherForActivityResult(ScanContract()) { result ->
        if (result.contents.isNullOrBlank()) scannerMessage = "QR scan cancelled. You can enter the code manually."
        else { code = result.contents; scannerMessage = "Pairing code scanned successfully." }
    }
    val cameraPermission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        if (granted) scanner.launch(ScanOptions().setDesiredBarcodeFormats(ScanOptions.QR_CODE).setPrompt("Scan the laptop pairing QR code").setBeepEnabled(false).setOrientationLocked(false))
        else scannerMessage = "Camera permission is required to scan a QR code. Enter the code manually instead."
    }

    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        Text("Link this phone", style = MaterialTheme.typography.headlineMedium)
        Text(if (pending) "Pairing request sent. Keep this app open until the laptop accepts it." else "Scan the QR code shown by the laptop or enter its pairing code manually.")
        OutlinedTextField(value = code, onValueChange = { code = it }, label = { Text("Pairing code") }, singleLine = true, enabled = !pending)
        OutlinedButton(enabled = !pending, onClick = { cameraPermission.launch(Manifest.permission.CAMERA) }) { Text("Scan laptop QR code") }
        OutlinedTextField(value = name, onValueChange = { name = it }, label = { Text("Phone name") }, singleLine = true, enabled = !pending)
        Button(enabled = !pending && code.isNotBlank(), onClick = { onPair(code, name) }) { Text("Request link") }
        if (pending) OutlinedButton(onClick = onCancel) { Text("Cancel pairing request") }
        if (status.isNotBlank()) Text(status, color = MaterialTheme.colorScheme.primary)
        if (scannerMessage.isNotBlank()) Text(scannerMessage, color = MaterialTheme.colorScheme.secondary)
        Text("Pairing requests expire after ten minutes. The pairing code is private and links this phone to a laptop.", style = MaterialTheme.typography.bodySmall)
    }
}
