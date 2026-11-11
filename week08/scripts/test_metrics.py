"""Hand-check strict parsing and frozen input corruption detection."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('train',ROOT/'week08/train.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class MetricsTest(unittest.TestCase):
    def test_strict_json_and_wrong_fields(self):
        answer={'total':'12.30','currency':'USD'}
        rows=[{'answer':answer,'prediction':x} for x in [
            '{"currency":"USD","total":"12.30"}',
            'Here is JSON: {"total":"12.30","currency":"USD"}',
            '{"total":12.3,"currency":"USD"}',
            '{"total":"12.30","currency":"EUR"}', '[]']]
        result=m.score(rows)
        self.assertEqual(result['exact_rate'],1/5)
        self.assertEqual(result['json_valid_rate'],3/5)
        self.assertEqual(result['total_correct_rate'],2/5)
        self.assertEqual(result['currency_correct_rate'],2/5)

    def test_corrupt_data_rejected(self):
        import json
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'week08/data').mkdir(parents=True)
            path=root/'input.jsonl'; path.write_text('changed')
            (root/'week08/data/freeze.json').write_text(json.dumps({'files':{'input.jsonl':{'sha256':'wrong'}}}))
            with patch.object(m,'ROOT',root), self.assertRaisesRegex(ValueError,'hash mismatch'):
                m.verify_data()

if __name__=='__main__':
    unittest.main()
