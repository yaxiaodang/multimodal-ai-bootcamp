"""校验冻结输入，评价一轮完整 Docling 输出；不修改原始结果。"""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
WEEK=ROOT/'week07'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s): return ''.join(c for c in unicodedata.normalize('NFKC',s).casefold() if c.isalnum())
def similarity(a,b):
    a,b=norm(a),norm(b)
    previous=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        current=[i]
        for j,y in enumerate(b,1): current.append(min(current[-1]+1,previous[j]+1,previous[j-1]+(x!=y)))
        previous=current
    return 1-previous[-1]/max(len(a),len(b),1)
def extract(data):
    blocks=[]
    def visit(ref):
        value=data
        for key in ref.removeprefix('#/').split('/'):
            value=value[int(key)] if isinstance(value,list) else value[key]
        if ref.startswith('#/tables/'):
            cells=value['data']['table_cells']
            unique={}
            for c in cells:
                unique.setdefault((c['start_row_offset_idx'],c['start_col_offset_idx']),c['text'])
            blocks.extend(unique[k] for k in sorted(unique))
        elif 'text' in value: blocks.append(value['text'])
        else:
            for child in value.get('children',[]): visit(child['$ref'])
    for child in data['body']['children']: visit(child['$ref'])
    return blocks

def table_exact(data, ref):
    tables=data.get('tables',[])
    if len(tables)!=1: return False
    t=tables[0]['data']; expected=ref['table_grid']
    if (t['num_rows'],t['num_cols'])!=(len(expected),len(expected[0])): return False
    cells={(c['start_row_offset_idx'],c['start_col_offset_idx']):c for c in t['table_cells']}
    for r,row in enumerate(expected):
        for col,text in enumerate(row):
            if text and ((r,col) not in cells or norm(cells[r,col]['text'])!=norm(text)): return False
    spans=sorted([c['start_row_offset_idx'],c['end_row_offset_idx'],c['start_col_offset_idx'],c['end_col_offset_idx']] for c in cells.values() if c['row_span']>1 or c['col_span']>1)
    return spans==sorted(ref['table_spans'])
def verify():
    freeze=json.loads((WEEK/'data/freeze.json').read_text())
    for path,expected in freeze['files'].items():
        if sha(ROOT/path)!=expected: raise ValueError(f'冻结文件被修改：{path}')
    test=json.loads((WEEK/'data/test-manifest.json').read_text())['documents']
    dev=json.loads((WEEK/'data/dev-manifest.json').read_text())['documents']
    if len(test)!=24 or len({d['id'] for d in test+dev})!=27: raise ValueError('样例数/ID 错误')
    old=[sha(p) for p in (ROOT/'week05/samples').glob('*.pdf')]
    if set(d['sha256'] for d in test)&set(old+[d['sha256'] for d in dev]): raise ValueError('输入重复泄漏')
    return test

def evaluate(run):
    docs=verify()
    metadata=json.loads((run/'run-metadata.json').read_text())
    records={d['id']:d for d in metadata['documents']}
    if set(records)!={d['id'] for d in docs}: raise ValueError('运行必须包含全部24个样例，包括失败项')
    if metadata['config']!=json.loads((WEEK/'configs/baseline.json').read_text()): raise ValueError('baseline 配置不一致')
    snapshot=run/'snapshots/week07/data/test-manifest.json'
    if sha(snapshot)!=sha(WEEK/'data/test-manifest.json'): raise ValueError('运行输入清单不一致')
    rows=[]
    for d in docs:
        record=records[d['id']]
        if record['input_sha256']!=d['sha256']: raise ValueError('运行输入哈希不一致')
        ref=json.loads((ROOT/d['reference']).read_text())
        folder=run/d['id']; data={}; blocks=[]
        # Authenticate raw outputs against the producer's receipt before scoring.
        for item in record.get('output_files',[]):
            if sha(run/item['file'])!=item['sha256']: raise ValueError(f'原始输出被修改：{item["file"]}')
        success=record['status']=='completed'
        if success:
            data=json.loads((folder/'document.json').read_text()); blocks=extract(data)
        prediction=''.join(blocks); markers=[norm(x) for x in ref['reading_order']]
        positions=[norm(prediction).find(x) for x in markers]
        pairs=[positions[i]>=0 and positions[j]>positions[i] for i in range(len(markers)) for j in range(i+1,len(markers))]
        rows.append({'id':d['id'],'type':d['type'],'layout':d['layout'],'scan_quality':d['scan_quality'],
                     'success':success,'score':similarity(''.join(ref['blocks']),prediction) if success else 0,
                     'reading_order':sum(pairs)/len(pairs) if pairs else None,
                     'table_exact':table_exact(data,ref) if ref['table_grid'] and success else False if ref['table_grid'] else None,
                     'elapsed_seconds':record['elapsed_seconds'],'reference_blocks':ref['blocks'],'prediction_blocks':blocks})
    def aggregate(items):
        return {'n':len(items),'score':sum(x['score'] for x in items)/len(items),'success_rate':sum(x['success'] for x in items)/len(items),
                'reading_order':mean([x['reading_order'] for x in items if x['reading_order'] is not None]),
                'table_exact':mean([x['table_exact'] for x in items if x['table_exact'] is not None]),
                'total_seconds':sum(x['elapsed_seconds'] for x in items)}
    result={'run':str(run.relative_to(ROOT)),'freeze_sha256':sha(WEEK/'data/freeze.json'), 'overall':aggregate(rows),
            'slices':{key:{str(v):aggregate([x for x in rows if x[key]==v]) for v in sorted({x[key] for x in rows},key=str) if v is not None} for key in ['type','layout','scan_quality']},
            'worst_five':[x['id'] for x in sorted(rows,key=lambda x:(x['score'],x['id']))[:5]],'documents':rows}
    output=run/'evaluation.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['overall','slices','worst_five']},ensure_ascii=False,indent=2))
    return result

def mean(xs): return sum(xs)/len(xs) if xs else None
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--verify-only',action='store_true',help='只校验冻结哈希和输入重复，不推理'); p.add_argument('--run',type=Path,help='明确指定完整运行目录')
    args=p.parse_args()
    try:
        if args.verify_only: verify(); print('冻结哈希和精确重复检查通过；模板相似性不由哈希排除。')
        elif args.run: evaluate(args.run.resolve())
        else: p.error('请提供 --verify-only 或 --run')
    except (OSError,ValueError,KeyError) as error: p.exit(2,f'评测拒绝：{error}\n')
