package com.rustraid.data
import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
private val Context.store by preferencesDataStore("rustraid")
class PreferencesManager(private val context:Context){
 private val customSound=stringPreferencesKey("custom_sound_uri")
 val customSoundUri:Flow<String> = context.store.data.map{it[customSound]?:""}
 suspend fun setCustomSoundUri(uri:String){context.store.edit{it[customSound]=uri}}
 suspend fun getCustomSoundUri()=customSoundUri.first()
}
