package com.rustraid.model
data class AppSettings(val alertMode:String="critical",val cooldownMinutes:Int=120,val screenFlash:Boolean=true,val vibration:Boolean=true)
