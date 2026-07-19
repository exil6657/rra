package com.rustraid.ui.screens

import android.Manifest
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.journeyapps.barcodescanner.ScanContract
import com.journeyapps.barcodescanner.ScanOptions
import com.rustraid.ui.components.CommandCard
import com.rustraid.ui.components.TypewriterText
import com.rustraid.ui.theme.*

@Composable
fun PairingScreen(pending:Boolean,status:String,onPair:(String,String)->Unit,onCancel:()->Unit){
    var code by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("${Build.MANUFACTURER} ${Build.MODEL}".trim()) }
    var scannerMessage by remember { mutableStateOf("") }
    val scanner=rememberLauncherForActivityResult(ScanContract()){result->if(result.contents.isNullOrBlank())scannerMessage="SCAN CANCELLED // MANUAL CODE AVAILABLE" else {code=result.contents;scannerMessage="QR CODE ACQUIRED"}}
    val cameraPermission=rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()){granted->if(granted)scanner.launch(ScanOptions().setDesiredBarcodeFormats(ScanOptions.QR_CODE).setPrompt("Scan PC pairing code").setBeepEnabled(false).setOrientationLocked(false)) else scannerMessage="CAMERA DENIED // ENTER CODE MANUALLY"}
    Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(20.dp),verticalArrangement=Arrangement.spacedBy(14.dp)) {
        Text("RUST RAID",style=MaterialTheme.typography.headlineLarge);TypewriterText("// PAIR THIS PHONE TO A PC",color=PurpleSoft)
        CommandCard("PAIRING STATUS",if(pending)Orange else Purple,Modifier.fillMaxWidth()) { Text(if(pending)"REQUEST PENDING" else "AWAITING PC PAIR CODE",style=MaterialTheme.typography.headlineSmall);Text(if(pending)"Keep the PC app running while it verifies this phone." else "Scan the PC QR code or enter the full pairing code.",color=Muted) }
        CommandCard("LINK CREDENTIALS",Purple,Modifier.fillMaxWidth()) {
            OutlinedTextField(value=code,onValueChange={code=it},label={Text("PAIRING CODE")},singleLine=true,enabled=!pending,modifier=Modifier.fillMaxWidth())
            OutlinedButton(enabled=!pending,onClick={cameraPermission.launch(Manifest.permission.CAMERA)},modifier=Modifier.fillMaxWidth()){Text("⌁  SCAN PC QR CODE",style=MaterialTheme.typography.labelLarge)}
            OutlinedTextField(value=name,onValueChange={name=it},label={Text("DEVICE NAME")},singleLine=true,enabled=!pending,modifier=Modifier.fillMaxWidth())
            Button(enabled=!pending&&code.isNotBlank(),onClick={onPair(code,name)},modifier=Modifier.fillMaxWidth()){Text("LINK TO PC",style=MaterialTheme.typography.labelLarge)}
            if(pending)OutlinedButton(onClick=onCancel,modifier=Modifier.fillMaxWidth()){Text("CANCEL REQUEST")}
        }
        if(status.isNotBlank())Text(status,color=MaterialTheme.colorScheme.primary,style=MaterialTheme.typography.labelLarge)
        if(scannerMessage.isNotBlank())Text(scannerMessage,color=MaterialTheme.colorScheme.secondary,style=MaterialTheme.typography.labelLarge)
        Spacer(Modifier.weight(1f));Text("ONE-TIME CODES EXPIRE IN 10 MINUTES",color=Muted,style=MaterialTheme.typography.labelSmall)
    }
}
