@echo off
py -3.11 -m pip install -r requirements.txt pyinstaller
py -3.11 -m PyInstaller --noconfirm --windowed --name RustRaidAlarm --add-data "assets;assets" --add-data "ui/styles;ui/styles" main.py
echo Build complete: dist\RustRaidAlarm\RustRaidAlarm.exe
