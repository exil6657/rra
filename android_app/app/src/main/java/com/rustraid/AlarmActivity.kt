package com.rustraid
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.rustraid.data.FirebaseRepository
import com.rustraid.service.AlarmService
import com.rustraid.ui.screens.AlarmScreen
import com.rustraid.ui.screens.SilentAlertScreen
import com.rustraid.ui.theme.RustRaidTheme
class AlarmActivity:ComponentActivity(){
 override fun onCreate(state:Bundle?){super.onCreate(state);val silent=intent.getBooleanExtra(AlarmService.EXTRA_SILENT,false);val flash=intent.getBooleanExtra(AlarmService.EXTRA_FLASH,true);setShowWhenLocked(true);setTurnScreenOn(true);window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);setContent{RustRaidTheme{val acknowledge={FirebaseRepository().acknowledge();stopService(AlarmService.intent(this));finish()};if(silent)SilentAlertScreen(acknowledge) else AlarmScreen(flash,acknowledge)}}}
}
