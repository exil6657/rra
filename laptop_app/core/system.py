"""Small OS integrations with explicit opt-in and safe no-op behavior off Windows."""
import os
import sys
from pathlib import Path

def set_windows_autostart(enabled: bool) -> bool:
    """Create/remove a current-user Run key. Returns False on non-Windows or registry failure."""
    if os.name != 'nt': return False
    try:
        import winreg
        key_path=r'Software\Microsoft\Windows\CurrentVersion\Run'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,key_path,0,winreg.KEY_SET_VALUE) as key:
            if enabled:
                executable=Path(sys.executable)
                entry=f'"{executable}" "{Path(__file__).resolve().parents[1] / "main.py"}"'
                winreg.SetValueEx(key,'RustRaidAlarm',0,winreg.REG_SZ,entry)
            else:
                try: winreg.DeleteValue(key,'RustRaidAlarm')
                except FileNotFoundError: pass
        return True
    except OSError: return False
