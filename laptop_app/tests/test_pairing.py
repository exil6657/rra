import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core import config
from core.pairing import ensure_laptop_identity, manual_pairing_code, pairing_payload, rotate_pair_secret
class PairingIdentityTests(unittest.TestCase):
 def test_identity_is_generated_once_and_persisted(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'config.json'
   with patch.object(config,'PATH',path):
    first=ensure_laptop_identity(config.load());second=ensure_laptop_identity(config.load())
  self.assertEqual(first['pairing']['laptop_id'],second['pairing']['laptop_id'])
  self.assertEqual(first['pairing']['pair_secret'],second['pairing']['pair_secret'])
  self.assertGreaterEqual(len(first['pairing']['pair_secret']),32)
 def test_rotating_secret_keeps_laptop_identity(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'config.json'
   with patch.object(config,'PATH',path):
    data=ensure_laptop_identity(config.load());identity=data['pairing']['laptop_id'];old=data['pairing']['pair_secret'];rotate_pair_secret(data)
  self.assertEqual(data['pairing']['laptop_id'],identity);self.assertNotEqual(data['pairing']['pair_secret'],old)
 def test_manual_code_contains_only_pairing_values(self):
  data=config.validate({'pairing':{'laptop_id':'laptop-1','pair_secret':'secret-value'}})
  self.assertEqual(pairing_payload(data),{'laptop_id':'laptop-1','pair_secret':'secret-value'})
  self.assertEqual(manual_pairing_code(data),'rra://pair/laptop-1/secret-value')
if __name__=='__main__':unittest.main()
