"""Per-PC identity, pairing secret, and multi-phone pairing helpers."""
from __future__ import annotations
import secrets
from uuid import uuid4
from core.config import load, save

def ensure_laptop_identity(config=None):
    config=config or load(); pairing=config.setdefault('pairing',{}); changed=False
    if not pairing.get('laptop_id'): pairing['laptop_id']=str(uuid4());changed=True
    if not pairing.get('pair_secret'): pairing['pair_secret']=secrets.token_urlsafe(32);changed=True
    if 'max_phones' not in pairing: pairing['max_phones']=1;changed=True
    if 'phones' not in pairing: pairing['phones']={};changed=True
    # Migrate old single-phone metadata without retaining credentials in local config.
    legacy_id=pairing.get('paired_phone_id','')
    if legacy_id and legacy_id not in pairing['phones']:
        pairing['phones'][legacy_id]={'name':pairing.get('paired_phone_name','Android phone'),'enabled':True};changed=True
    pairing.setdefault('paired_phone_id','');pairing.setdefault('paired_phone_name','')
    if changed: save(config)
    return config

def pairing_payload(config):
    pairing=config['pairing'];return {'laptop_id':pairing['laptop_id'],'pair_secret':pairing['pair_secret']}

def manual_pairing_code(config):
    payload=pairing_payload(config);return f"rra://pair/{payload['laptop_id']}/{payload['pair_secret']}"

def rotate_pair_secret(config):
    config['pairing']['pair_secret']=secrets.token_urlsafe(32);save(config);return config

def phones(config): return config['pairing'].setdefault('phones',{})
def phone_limit(config): return max(1,min(5,int(config['pairing'].get('max_phones',1))))
def can_accept_phone(config, phone_id): return phone_id in phones(config) or len(phones(config)) < phone_limit(config)
