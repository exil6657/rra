@echo off
setlocal
py -3.11 -m pip install -r requirements.txt pyinstaller
py -3.11 -m PyInstaller --noconfirm --clean --windowed --name RustRaidAlarm --paths . --add-data "assets;assets" --add-data "ui/styles;ui/styles" --collect-all pygame --collect-all pytesseract --collect-all cv2 --collect-all mss --collect-all qrcode --collect-all firebase_admin main.py
if errorlevel 1 exit /b %errorlevel%
echo.
echo Build complete: dist\RustRaidAlarm\RustRaidAlarm.exe
echo User configuration and logs are stored in %%APPDATA%%\RustRaidAlarm when running the EXE.
endlocal
