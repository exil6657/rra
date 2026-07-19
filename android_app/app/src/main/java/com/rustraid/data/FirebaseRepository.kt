package com.rustraid.data
import com.google.firebase.database.FirebaseDatabase
class FirebaseRepository { private val root=FirebaseDatabase.getInstance().reference; fun acknowledge(){root.child("raid_alarm").updateChildren(mapOf("alarm_active" to false,"acknowledged" to true,"acknowledged_by" to "phone"))}; fun setMode(mode:String){root.child("settings/alert_mode").setValue(mode)} }
