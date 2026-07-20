package com.rustraid.model
data class AlertSnapshot(
 val state:AlertState=AlertState.DISCONNECTED,
 val triggeredAt:String?=null,
 val cooldownUntil:String?=null,
 val message:String=""
)
