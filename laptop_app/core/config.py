"""Atomic, local configuration storage. Secrets never leave this machine except Firebase setup."""
import json, os, tempfile
from pathlib import Path
from copy import deepcopy
ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config.json"
DEFAULT = {"disclaimer_accepted":False,"setup_complete":False,"discord":{"bot_token":"","channel_id":"","user_id":"","channel_name":""},"firebase":{"service_account_json":"","database_url":""},"alarm":{"device_target":"both","active_preset":"defcon1","volume":100,"tts_enabled":True,"screen_flash":True,"flash_color":"#FF2D2D","custom_sound":"","custom_tts":"WE ARE BEING RAIDED"},"cooldown":{"duration_minutes":120,"auto_silence_minutes":5,"quiet_hours_enabled":False,"quiet_hours_start":"23:00","quiet_hours_end":"07:00"},"integrations":{"snap_enabled":False,"snap_username":"","snap_message":"WE ARE BEING RAIDED — GET ON!","discord_dm_enabled":False,"discord_friend_id":"","discord_dm_message":"RAID ALERT Get on Rust NOW"},"app":{"start_with_windows":False,"start_minimized":False},"screen_monitor":{"enabled":False,"region":{"x":0,"y":0,"width":0,"height":0},"trigger_text":"","template_path":"","template_threshold":0.88,"poll_interval_ms":400,"confirm_frames":2},"activity":[]}
def merge(base, incoming):
    for k,v in incoming.items(): base[k] = merge(base.get(k,{}),v) if isinstance(v,dict) and isinstance(base.get(k),dict) else v
    return base
def load():
    if not PATH.exists(): return deepcopy(DEFAULT)
    try:
        return merge(deepcopy(DEFAULT), json.loads(PATH.read_text(encoding='utf-8')))
    except (json.JSONDecodeError,OSError): return deepcopy(DEFAULT)
def save(data):
    PATH.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=PATH.parent, prefix='config-', suffix='.json')
    with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(data,f,indent=2,ensure_ascii=False)
    os.replace(tmp,PATH)
def update(section, values):
    data=load(); data[section].update(values); save(data); return data
