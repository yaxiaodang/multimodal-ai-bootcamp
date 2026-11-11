"""针对计分、顺序与冻结保护的手算测试，不运行模型。"""
import unittest
import tempfile
import json
from pathlib import Path
import evaluate as e
class EvaluationTests(unittest.TestCase):
    def test_hand_calculated_edit(self):
        self.assertAlmostEqual(e.similarity('abc','adc'),2/3)
        self.assertEqual(e.similarity('Ａ B，c','abc'),1)
        self.assertEqual(e.similarity('abc',''),0)
        self.assertLess(e.similarity('甲乙丙','丙乙甲'),1)
    def test_body_order_and_table_anchors(self):
        data={'body':{'children':[{'$ref':'#/texts/1'},{'$ref':'#/tables/0'},{'$ref':'#/texts/0'}]},
              'texts':[{'text':'末'},{'text':'首'}], 'tables':[{'data':{'table_cells':[
                  {'start_row_offset_idx':0,'start_col_offset_idx':0,'text':'表'},
                  {'start_row_offset_idx':0,'start_col_offset_idx':0,'text':'表'}]}}]}
        self.assertEqual(e.extract(data),['首','表','末'])
    def test_freeze_detects_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); (root/'data').mkdir(); (root/'item').write_text('changed')
            (root/'data/freeze.json').write_text(json.dumps({'files':{'item':'wrong hash'}}))
            oldroot,oldweek=e.ROOT,e.WEEK
            try:
                e.ROOT=e.WEEK=root
                with self.assertRaisesRegex(ValueError,'冻结文件被修改'): e.verify()
            finally: e.ROOT,e.WEEK=oldroot,oldweek
    def test_merge_structure_not_just_numbers(self):
        ref={'table_grid':[['A',''],['B','C']],'table_spans':[[0,1,0,2]]}
        def cell(r,c,text,end=1):
            return {'start_row_offset_idx':r,'end_row_offset_idx':r+1,'start_col_offset_idx':c,
                    'end_col_offset_idx':c+end,'text':text,'row_span':1,'col_span':end}
        data={'tables':[{'data':{'num_rows':2,'num_cols':2,'table_cells':[cell(0,0,'A',2),cell(1,0,'B'),cell(1,1,'C')]}}]}
        self.assertTrue(e.table_exact(data,ref))
        data['tables'][0]['data']['table_cells'][0]=cell(0,0,'A')
        self.assertFalse(e.table_exact(data,ref))
if __name__=='__main__': unittest.main(verbosity=2)
