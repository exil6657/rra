"""Validated atomic local configuration storage."""
import json, os, tempfile
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'config.json'
DEFAULT={"disclaimer_accepted":False,"setup_complete":False,"discord":{"bot_token":"","channel_id":"","user_id":"","channel_name":""},"firebase":{"service_account_json":"","database_url":""},"alarm":{"device_target":"both","active_preset":"defcon1","volume":100,"tts_enabled":True,"screen_flash":True,"flash_color":"#FF2D2D","custom_sound":"","custom_tts":"WE ARE BEING RAIDED"},"cooldown":{"duration_minutes":120,"auto_silence_minutes":5,"quiet_hours_enabled":False,"quiet_hours_start":"23:00","quiet_hours_end":"07:00"},"integrations":{"snap_enabled":False,"snap_username":"","snap_message":"WE ARE BEING RAIDED — GET ON!","discord_dm_enabled":False,"discord_friend_id":"","discord_dm_message":"RAID ALERT Get on Rust NOW"},"app":{"start_with_windows":False,"start_minimized":False,"phone_alert_mode":"critical","phone_vibration":True,"phone_screen_flash":True},"pairing":{"laptop_id":"","pair_secret":"","paired_phone_id":"","paired_phone_name":""},"screen_monitor":{"enabled":False,"region":{"x":0,"y":0,"width":0,"height":0},"trigger_text":"","template_path":"","template_threshold":0.88,"poll_interval_ms":400,"confirm_frames":2},"activity":[]}
def merge(base,incoming):
    for key,value in incoming.items():base[key]=merge(base.get(key,{}),value) if isinstance(value,dict) and isinstance(base.get(key),dict) else value
    return base
def validate(data):
    """Validate backup shape and return a complete normalized copy, never mutating caller data."""
    if not isinstance(data,dict):raise ValueError('Configuration root must be a JSON object.')
    for section in ('alarm','cooldown','firebase','app','screen_monitor'):
        if section in data and not isinstance(data[section],dict):raise ValueError(f'Configuration section {section!r} must be an object.')
    monitor=data.get('screen_monitor',{});region=monitor.get('region',{})
    if region and (not isinstance(region,dict) or any(not isinstance(region.get(key,0),int) for key in ('x','y','width','height'))):raise ValueError('Screen-monitor region coordinates must be integers.')
    alarm=data.get('alarm',{});volume=alarm.get('volume',100)
    if not isinstance(volume,int) or not 0<=volume<=100:raise ValueError('Alarm volume must be an integer from 0 to 100.')
    return merge(deepcopy(DEFAULT),deepcopy(data))
def load():
    if not PATH.exists():return deepcopy(DEFAULT)
    try:return validate(json.loads(PATH.read_text(encoding='utf-8')))
    except (json.JSONDecodeError,OSError,ValueError):return deepcopy(DEFAULT)
def save(data):
    normalized=validate(data);PATH.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=PATH.parent,prefix='config-',suffix='.json')
    with os.fdopen(fd,'w',encoding='utf-8') as file:json.dump(normalized,file,indent=2,ensure_ascii=False)
    os.replace(tmp,PATH)
def update(section,values):
    data=load();data[section].update(values);save(data);return load()
def reset(keep_disclaimer=True):
    data=deepcopy(DEFAULT)
    if keep_disclaimer:data['disclaimer_accepted']=load().get('disclaimer_accepted',False)
    save(data);return data
