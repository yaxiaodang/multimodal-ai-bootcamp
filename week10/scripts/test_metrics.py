"""Hand-calculable metric boundary tests; no model loading."""
import unittest
from common import pdf, score


class Metrics(unittest.TestCase):
    def test_edit_distance_and_sequence(self):
        self.assertAlmostEqual(pdf.similarity('abc','axc'),2/3)
        self.assertLess(pdf.similarity('ab','ba'),1)
        self.assertEqual(pdf.similarity('ABC !','abc'),1)
        self.assertEqual(pdf.similarity('abc',''),0)

    def test_json_strict_fields(self):
        answer = {'total':'1.00','currency':'USD'}
        rows = [{'answer':answer,'prediction':s} for s in ['{"currency":"USD", "total":"1.00"}', '{"currency":"USD","total":1}', '{"currency":"USD","total":"1.00","x":0}', '[]', 'garbage']]
        m = score(rows)
        self.assertEqual(m['exact_rate'],1/5)
        self.assertEqual(m['json_valid_rate'],3/5)


if __name__ == '__main__':
    unittest.main()
