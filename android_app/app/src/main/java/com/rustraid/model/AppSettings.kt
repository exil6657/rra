package com.rustraid.model
data class AppSettings(
 val alertMode:String="critical",
 val cooldownMinutes:Int=120,
 val screenFlash:Boolean=true,
 val vibration:Boolean=true,
 val quietHoursEnabled:Boolean=false,
 val autoSilenceMinutes:Int=5,
 val amoledBlack:Boolean=false
)
