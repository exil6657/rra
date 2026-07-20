package com.rustraid.model
data class AppSettings(
 val alertMode:String="critical",
 val deviceTarget:String="both",
 val cooldownMinutes:Int=120,
 val screenFlash:Boolean=true,
 val vibration:Boolean=true,
 val volumeOverride:Boolean=true,
 val phoneSoundPreset:String="defcon1",
 val quietHoursEnabled:Boolean=false,
 val quietHoursStart:String="23:00",
 val quietHoursEnd:String="07:00",
 val autoSilenceMinutes:Int=5,
 val amoledBlack:Boolean=false,
 val keepScreenOnDuringCooldown:Boolean=false
)
