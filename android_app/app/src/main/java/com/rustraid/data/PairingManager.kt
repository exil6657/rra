package com.rustraid.data
import android.content.Context
import android.os.Handler
import android.os.Looper
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.google.firebase.database.FirebaseDatabase
import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.messaging.FirebaseMessaging
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import java.util.UUID
private val Context.pairingStore by preferencesDataStore("rustraid_pairing")
data class PairingInfo(val laptopId:String="",val phoneId:String="",val phoneName:String="Android phone",val pendingSecret:String="") { val linked:Boolean get()=laptopId.isNotBlank() && pendingSecret.isBlank() }
class PairingManager(private val context:Context){
 private val mainHandler=Handler(Looper.getMainLooper())
 private val laptopId=stringPreferencesKey("laptop_id");private val phoneId=stringPreferencesKey("phone_id");private val phoneName=stringPreferencesKey("phone_name");private val pendingSecret=stringPreferencesKey("pending_secret")
 val info:Flow<PairingInfo> = context.pairingStore.data.map { PairingInfo(it[laptopId]?:"",it[phoneId]?:"",it[phoneName]?:"Android phone",it[pendingSecret]?:"") }
 suspend fun request(code:String,name:String,onResult:(Result<Unit>)->Unit){
  val parts=code.trim().removePrefix("rra://pair/").split('/');if(parts.size!=2||parts.any{it.isBlank()}){onResult(Result.failure(IllegalArgumentException("Use the full pairing code shown by the laptop.")));return}
  val id=parts[0];val secret=parts[1];val authUid=FirebaseAuth.getInstance().currentUser?.uid?:run{onResult(Result.failure(IllegalStateException("Firebase authentication is still starting. Try again in a moment.")));return};val thisPhone=UUID.randomUUID().toString();FirebaseMessaging.getInstance().token.addOnSuccessListener { token ->
   FirebaseDatabase.getInstance().getReference("pair_requests").child(id).child(thisPhone).setValue(mapOf("pair_secret" to secret,"fcm_token" to token,"phone_name" to name,"auth_uid" to authUid,"requested_at" to System.currentTimeMillis())).addOnSuccessListener {
    kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch { context.pairingStore.edit { prefs->prefs[laptopId]=id;prefs[phoneId]=thisPhone;prefs[phoneName]=name;prefs[pendingSecret]=secret };mainHandler.post{onResult(Result.success(Unit))} }
   }.addOnFailureListener{error->mainHandler.post{onResult(Result.failure(error))}}
  }.addOnFailureListener{error->mainHandler.post{onResult(Result.failure(error))}}
 }
 suspend fun confirmLinked(){context.pairingStore.edit{it.remove(pendingSecret)}}
 suspend fun cancelPending(info:PairingInfo){
  if(info.laptopId.isNotBlank()&&info.phoneId.isNotBlank())FirebaseDatabase.getInstance().getReference("pair_requests").child(info.laptopId).child(info.phoneId).removeValue()
  context.pairingStore.edit{it.clear()}
 }
 fun refreshFcmToken(token:String){
  kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
   val pairing=info.first();val uid=FirebaseAuth.getInstance().currentUser?.uid?:return@launch
   if(pairing.linked)FirebaseDatabase.getInstance().getReference("token_refresh_requests").child(pairing.laptopId).child(pairing.phoneId).setValue(mapOf("auth_uid" to uid,"fcm_token" to token,"requested_at" to System.currentTimeMillis()))
  }
 }
 suspend fun requestUnlink(info:PairingInfo,onResult:(Result<Unit>)->Unit){
  if(!info.linked){onResult(Result.success(Unit));return}
  val uid=FirebaseAuth.getInstance().currentUser?.uid?:run{onResult(Result.failure(IllegalStateException("Firebase authentication unavailable.")));return}
  FirebaseDatabase.getInstance().getReference("unlink_requests").child(info.laptopId).child(info.phoneId).setValue(mapOf("auth_uid" to uid,"requested_at" to System.currentTimeMillis())).addOnSuccessListener { mainHandler.post{onResult(Result.success(Unit))} }.addOnFailureListener{mainHandler.post{onResult(Result.failure(it))}}
 }
 suspend fun unlink(){context.pairingStore.edit{it.clear()}}
}
