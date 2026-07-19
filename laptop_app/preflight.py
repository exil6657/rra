"""Local installation readiness check. Run before configuring Rust Raid Alarm."""
from __future__ import annotations
import importlib
import json
import platform
import sys
import wave
from pathlib import Path
from core.config import CONFIG_DIR, load

ROOT=Path(__file__).resolve().parent
REQUIRED=("PyQt6","pygame","pyttsx3","firebase_admin","mss","cv2","pytesseract","qrcode")

def check(label, ok, detail=""):
    marker="PASS" if ok else "FAIL"
    print(f"[{marker}] {label}"+(f" — {detail}" if detail else ""))
    return ok

def main():
    print("Rust Raid Alarm preflight check")
    print(f"Python: {sys.version.split()[0]} | OS: {platform.platform()}")
    passed=True
    passed &= check("Python 3.11+",sys.version_info>=(3,11),"install Python 3.11 or newer" if sys.version_info<(3,11) else "")
    for module in REQUIRED:
        try: importlib.import_module(module); check(module,True)
        except Exception as exc: passed=False;check(module,False,str(exc))
    try:
        import pytesseract
        version=str(pytesseract.get_tesseract_version()).splitlines()[0]
        check("Tesseract OCR engine",True,version)
    except Exception as exc:
        passed=False;check("Tesseract OCR engine",False,"install Tesseract and add it to PATH: "+str(exc))
    for name in ("defcon1.wav","tactical.wav","stealth.wav"):
        path=ROOT/"assets"/"sounds"/name
        try:
            with wave.open(str(path)) as audio: valid=audio.getnframes()>0 and audio.getframerate()>0
            passed &= check(f"Bundled sound {name}",valid)
        except Exception as exc:
            passed=False;check(f"Bundled sound {name}",False,str(exc))
    data=load();firebase=data["firebase"]
    check("Runtime data directory",True,str(CONFIG_DIR))
    check("Firebase database configured",bool(firebase.get("database_url")),"configure later in Settings → Integrations" if not firebase.get("database_url") else "")
    check("Firebase service account configured",bool(firebase.get("service_account_json")),"configure later in Settings → Integrations" if not firebase.get("service_account_json") else "")
    print("\nReady." if passed else "\nFix the failed checks before relying on alarm monitoring.")
    return 0 if passed else 1
if __name__=="__main__": raise SystemExit(main())
