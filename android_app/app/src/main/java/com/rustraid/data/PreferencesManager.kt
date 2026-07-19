package com.rustraid.data
import android.content.Context
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
private val Context.store by preferencesDataStore("rustraid")
class PreferencesManager(private val context:Context){private val mode=stringPreferencesKey("mode"); val alertMode:Flow<String> = context.store.data.map{it[mode]?:"critical"}; suspend fun setAlertMode(v:String){context.store.edit{it[mode]=v}}}
