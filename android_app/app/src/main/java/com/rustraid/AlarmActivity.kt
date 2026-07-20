package com.rustraid
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.google.firebase.database.ValueEventListener
import com.rustraid.data.FirebaseRepository
import com.rustraid.model.AlertState
import com.rustraid.service.AlarmService
import com.rustraid.ui.screens.AlarmScreen
import com.rustraid.ui.screens.SilentAlertScreen
import com.rustraid.ui.theme.RustRaidTheme
class AlarmActivity:ComponentActivity(){
 private var alarmListener:ValueEventListener?=null;private var repository:FirebaseRepository?=null
 override fun onCreate(state:Bundle?){super.onCreate(state);val laptopId=intent.getStringExtra(AlarmService.EXTRA_LAPTOP_ID)?:"";val silent=intent.getBooleanExtra(AlarmService.EXTRA_SILENT,false);val flash=intent.getBooleanExtra(AlarmService.EXTRA_FLASH,true);setShowWhenLocked(true);setTurnScreenOn(true);window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
  if(laptopId.isNotBlank()){repository=FirebaseRepository(laptopId);alarmListener=repository!!.watchAlarm({snapshot->if(snapshot.state!=AlertState.RAID_ACTIVE)runOnUiThread{finish()}},{})}
  setContent{RustRaidTheme{val acknowledge={if(laptopId.isNotBlank())FirebaseRepository(laptopId).acknowledge();stopService(AlarmService.intent(this,laptopId=laptopId));finish()};if(silent)SilentAlertScreen(acknowledge) else AlarmScreen(flash,acknowledge)}}
 }
 override fun onDestroy(){alarmListener?.let{repository?.removeAlarmListener(it)};window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);super.onDestroy()}
}
