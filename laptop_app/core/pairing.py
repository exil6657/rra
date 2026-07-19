"""Per-laptop identity and pairing-secret helpers.
The secret remains only in the laptop's local config. Firebase receives it only in a phone pairing
request and the laptop verifies it with a constant-time comparison before accepting a phone token.
"""
from __future__ import annotations
import secrets
from uuid import uuid4
from core.config import load, save

def ensure_laptop_identity(config=None):
    config=config or load(); pairing=config.setdefault('pairing',{})
    changed=False
    if not pairing.get('laptop_id'):
        pairing['laptop_id']=str(uuid4());changed=True
    if not pairing.get('pair_secret'):
        pairing['pair_secret']=secrets.token_urlsafe(32);changed=True
    pairing.setdefault('paired_phone_id','');pairing.setdefault('paired_phone_name','')
    if changed:save(config)
    return config

def pairing_payload(config):
    pairing=config['pairing']
    return {'laptop_id':pairing['laptop_id'],'pair_secret':pairing['pair_secret']}

def manual_pairing_code(config):
    """Readable URL used by QR and manual pairing; it is never written to Firebase."""
    payload=pairing_payload(config)
    return f"rra://pair/{payload['laptop_id']}/{payload['pair_secret']}"
