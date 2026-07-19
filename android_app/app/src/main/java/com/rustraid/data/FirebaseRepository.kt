package com.rustraid.data
import com.google.firebase.database.FirebaseDatabase
import java.time.Instant
class FirebaseRepository {
 private val root=FirebaseDatabase.getInstance().reference
 fun acknowledge(){
  root.child("settings/cooldown_duration_minutes").get().addOnSuccessListener { snap ->
   val minutes=(snap.getValue(Long::class.java)?:120L).coerceIn(1,1440)
   val until=Instant.ofEpochMilli(System.currentTimeMillis()+minutes*60_000).toString()
   root.child("raid_alarm").updateChildren(mapOf("alarm_active" to false,"acknowledged" to true,"acknowledged_by" to "phone","acknowledged_at" to Instant.now().toString(),"cooldown_until" to until))
  }.addOnFailureListener { root.child("raid_alarm").updateChildren(mapOf("alarm_active" to false,"acknowledged" to true,"acknowledged_by" to "phone")) }
 }
 fun setMode(mode:String){root.child("settings/alert_mode").setValue(mode)}
}
