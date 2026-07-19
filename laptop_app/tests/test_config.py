import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from core import config
class ConfigStorageTests(unittest.TestCase):
    def test_missing_config_returns_complete_defaults(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(config,'PATH',Path(tmp)/'missing.json'):
            data=config.load()
        self.assertIn('screen_monitor',data)
        self.assertIn('cooldown',data)
        self.assertFalse(data['screen_monitor']['enabled'])
    def test_partial_json_is_merged_with_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'config.json';path.write_text(json.dumps({'alarm':{'volume':37}}),encoding='utf-8')
            with patch.object(config,'PATH',path): data=config.load()
        self.assertEqual(data['alarm']['volume'],37)
        self.assertEqual(data['alarm']['active_preset'],'defcon1')
        self.assertIn('screen_monitor',data)
    def test_save_is_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'config.json'
            with patch.object(config,'PATH',path): config.save({'answer':42})
            self.assertEqual(json.loads(path.read_text(encoding='utf-8')),{'answer':42})
if __name__=='__main__': unittest.main()
