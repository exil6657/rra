package com.rustraid.data
import com.google.firebase.database.*
import com.rustraid.model.AlertSnapshot
import com.rustraid.model.AlertState
import com.rustraid.model.ActivityEntry
import java.time.Instant
class FirebaseRepository {
 private val root=FirebaseDatabase.getInstance().reference
 fun watchAlarm(onSnapshot:(AlertSnapshot)->Unit,onError:()->Unit):ValueEventListener{
  val listener=object:ValueEventListener{
   override fun onDataChange(s:DataSnapshot){
    val active=s.child("alarm_active").getValue(Boolean::class.java)?:false
    val cooldown=s.child("cooldown_until").getValue(String::class.java)
    val state=when{active->AlertState.RAID_ACTIVE; cooldown?.let{runCatching{Instant.parse(it).isAfter(Instant.now())}.getOrDefault(false)}==true->AlertState.COOLDOWN;else->AlertState.MONITORING}
    onSnapshot(AlertSnapshot(state,s.child("triggered_at").getValue(String::class.java),cooldown,s.child("message").getValue(String::class.java)?:""))
   }
   override fun onCancelled(error:DatabaseError){onError()}
  };root.child("raid_alarm").addValueEventListener(listener);return listener
 }
 fun watchActivity(onEntries:(List<ActivityEntry>)->Unit):ValueEventListener{
  val listener=object:ValueEventListener{
   override fun onDataChange(s:DataSnapshot){onEntries(s.children.map{child->ActivityEntry(child.key?:"",child.child("timestamp").getValue(String::class.java)?:"",child.child("description").getValue(String::class.java)?:"",child.child("type").getValue(String::class.java)?:"system")}.sortedByDescending{it.timestamp}.take(100))}
   override fun onCancelled(error:DatabaseError){}
  };root.child("activity_log/entries").addValueEventListener(listener);return listener
 }
 fun removeActivityListener(listener:ValueEventListener){root.child("activity_log/entries").removeEventListener(listener)}
 fun removeAlarmListener(listener:ValueEventListener){root.child("raid_alarm").removeEventListener(listener)}
 fun acknowledge(){root.child("settings/cooldown_duration_minutes").get().addOnSuccessListener { snap ->val minutes=(snap.getValue(Long::class.java)?:120L).coerceIn(1,1440);val until=Instant.ofEpochMilli(System.currentTimeMillis()+minutes*60_000).toString();root.child("raid_alarm").updateChildren(mapOf("alarm_active" to false,"acknowledged" to true,"acknowledged_by" to "phone","acknowledged_at" to Instant.now().toString(),"cooldown_until" to until))}.addOnFailureListener {root.child("raid_alarm").updateChildren(mapOf("alarm_active" to false,"acknowledged" to true,"acknowledged_by" to "phone"))}}
 fun setMode(mode:String){root.child("settings/alert_mode").setValue(mode)}
 fun triggerLocalTest(){root.child("raid_alarm").updateChildren(mapOf("alarm_active" to true,"acknowledged" to false,"triggered_at" to Instant.now().toString(),"message" to "Phone test alert"))}
}
