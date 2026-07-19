package com.rustraid.ui.screens
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.google.android.gms.codescanner.GmsBarcodeScannerOptions
import com.google.android.gms.codescanner.GmsBarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
@Composable fun PairingScreen(pending:Boolean,status:String,onPair:(String,String)->Unit,onCancel:()->Unit){
 var code by remember{mutableStateOf("")};var name by remember{mutableStateOf("Android phone")};val context=LocalContext.current
 Column(Modifier.fillMaxSize().padding(24.dp),verticalArrangement=Arrangement.spacedBy(14.dp)){
  Text("Link this phone",style=MaterialTheme.typography.headlineMedium)
  Text(if(pending)"Pairing request sent. Keep this app open until the laptop accepts it." else "Scan the QR code shown by the laptop or enter its pairing code manually.")
  OutlinedTextField(value=code,onValueChange={code=it},label={Text("Pairing code")},singleLine=true,enabled=!pending)
  Button(enabled=!pending,onClick={val options=GmsBarcodeScannerOptions.Builder().setBarcodeFormats(Barcode.FORMAT_QR_CODE).enableAutoZoom().build();GmsBarcodeScanning.getClient(context,options).startScan().addOnSuccessListener{barcode->code=barcode.rawValue?:""}.addOnFailureListener{}}){Text("Scan laptop QR code")}
  OutlinedTextField(value=name,onValueChange={name=it},label={Text("Phone name")},singleLine=true,enabled=!pending)
  Button(enabled=!pending&&code.isNotBlank(),onClick={onPair(code,name)}){Text("Request link")}
  if(pending)OutlinedButton(onClick=onCancel){Text("Cancel pairing request")}
  if(status.isNotBlank())Text(status,color=MaterialTheme.colorScheme.primary)
  Text("Pairing requests expire after ten minutes. The pairing code is private and links this phone to one laptop.",style=MaterialTheme.typography.bodySmall)
 }
}
