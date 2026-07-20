import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core import config
class ConfigStorageTests(unittest.TestCase):
 def test_missing_config_returns_complete_defaults(self):
  with tempfile.TemporaryDirectory() as tmp,patch.object(config,'PATH',Path(tmp)/'missing.json'):data=config.load()
  self.assertIn('screen_monitor',data);self.assertIn('cooldown',data);self.assertFalse(data['screen_monitor']['enabled'])
 def test_partial_json_is_merged_with_defaults(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'config.json';path.write_text(json.dumps({'alarm':{'volume':37}}),encoding='utf-8')
   with patch.object(config,'PATH',path):data=config.load()
  self.assertEqual(data['alarm']['volume'],37);self.assertEqual(data['alarm']['active_preset'],'defcon1');self.assertIn('screen_monitor',data)
 def test_save_normalizes_partial_config(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'config.json'
   with patch.object(config,'PATH',path):config.save({'alarm':{'volume':42}});saved=json.loads(path.read_text(encoding='utf-8'))
  self.assertEqual(saved['alarm']['volume'],42);self.assertIn('cooldown',saved)
 def test_invalid_backup_is_rejected(self):
  with self.assertRaises(ValueError):config.validate({'alarm':{'volume':101}})
  with self.assertRaises(ValueError):config.validate({'screen_monitor':{'region':{'x':'bad'}}})
 def test_reset_preserves_disclaimer_only_when_requested(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'config.json'
   with patch.object(config,'PATH',path):
    config.save({'disclaimer_accepted':True,'setup_complete':True,'alarm':{'volume':22},'activity':['old']});fresh=config.reset(keep_disclaimer=True)
  self.assertTrue(fresh['disclaimer_accepted']);self.assertFalse(fresh['setup_complete']);self.assertEqual(fresh['alarm']['volume'],100);self.assertEqual(fresh['activity'],[])
if __name__=='__main__':unittest.main()
