package com.rustraid.service
import android.content.Context
import android.content.Intent
/** User-controlled sharing only. This app never drives another app's UI or sends messages. */
object AutomationService { fun shareAlert(context:Context,message:String){context.startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_TEXT,message).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),"Share raid alert"))} }
