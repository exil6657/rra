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
  val id=parts[0];val secret=parts[1];val thisPhone=UUID.randomUUID().toString();FirebaseMessaging.getInstance().token.addOnSuccessListener { token ->
   FirebaseDatabase.getInstance().getReference("pair_requests").child(id).child(thisPhone).setValue(mapOf("pair_secret" to secret,"fcm_token" to token,"phone_name" to name,"auth_uid" to (FirebaseAuth.getInstance().currentUser?.uid?:""),"requested_at" to System.currentTimeMillis())).addOnSuccessListener {
    kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch { context.pairingStore.edit { prefs->prefs[laptopId]=id;prefs[phoneId]=thisPhone;prefs[phoneName]=name;prefs[pendingSecret]=secret };mainHandler.post{onResult(Result.success(Unit))} }
   }.addOnFailureListener{onResult(Result.failure(it))}
  }.addOnFailureListener{onResult(Result.failure(it))}
 }
 suspend fun confirmLinked(){context.pairingStore.edit{it.remove(pendingSecret)}}
 suspend fun unlink(){context.pairingStore.edit{it.clear()}}
}
