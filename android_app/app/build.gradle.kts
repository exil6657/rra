plugins { id("com.android.application"); id("org.jetbrains.kotlin.android"); id("com.google.gms.google-services") }
android { namespace="com.rustraid"; compileSdk=35
 defaultConfig { applicationId="com.rustraid"; minSdk=26; targetSdk=34; versionCode=1; versionName="1.0.0" }
}
dependencies { implementation(platform("androidx.compose:compose-bom:2024.09.03")); implementation("androidx.core:core-ktx:1.13.1"); implementation("androidx.activity:activity-compose:1.9.2"); implementation("androidx.compose.material3:material3"); implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.6"); implementation("androidx.datastore:datastore-preferences:1.1.1"); implementation(platform("com.google.firebase:firebase-bom:33.3.0")); implementation("com.google.firebase:firebase-database-ktx"); implementation("com.google.firebase:firebase-messaging-ktx") }
