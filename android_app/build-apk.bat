@echo off
setlocal
if not exist app\google-services.json (
  echo Missing app\google-services.json.
  echo Download it from Firebase Project Settings ^> Your apps ^> Android and copy it to android_app\app\google-services.json.
  exit /b 1
)
call gradlew.bat --no-daemon clean assembleDebug
if errorlevel 1 exit /b %errorlevel%
echo.
echo APK build complete:
echo %CD%\app\build\outputs\apk\debug\app-debug.apk
endlocal
