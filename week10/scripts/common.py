"""Shared scoring and input authentication; no model imports."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from week07.scripts import evaluate as pdf
from week08.train import score, verify_data


def read(path):
    return json.loads(Path(path).read_text())


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify():
    p = read(ROOT / 'week10/configs/protocol.json')
    for path, expected in p['files'].items():
        if sha(ROOT / path) != expected:
            raise ValueError(f'Protocol input changed: {path}')
    docs = pdf.verify()
    verify_data()
    a, b = [read(ROOT / p['text_runs'][k] / 'config.json') for k in ['run-a', 'run-b']]
    changed = [k for k in a if a[k] != b[k] and k != 'name']
    if changed != ['learning_rate']:
        raise ValueError(f'A/B must differ only in learning_rate: {changed}')
    baseline, ablation = [read(ROOT / f'week10/configs/{n}.json') for n in ['pdf-baseline', 'pdf-no-ocr']]
    if [k for k in baseline if baseline[k] != ablation[k] and k != 'name'] != ['do_ocr']:
        raise ValueError('PDF ablation must change only do_ocr')
    return p, docs


def aggregate(rows):
    def mean(key):
        values = [x[key] for x in rows if x.get(key) is not None]
        return sum(values) / len(values) if values else None
    return {'n': len(rows), **{k: mean(k) for k in ['score', 'success', 'reading_order', 'table_exact', 'exact', 'json_valid', 'total_correct', 'currency_correct']},
            'total_seconds': sum(x['seconds'] for x in rows)}


def slices(rows, keys):
    return {key: {str(v): aggregate([r for r in rows if r[key] == v])
                  for v in sorted({r[key] for r in rows}, key=str) if v is not None} for key in keys}


def pdf_rows(run, docs):
    """Week07 metric unchanged; authenticate every producer output receipt."""
    meta = read(run / 'run-metadata.json')
    records = {x['id']: x for x in meta['documents']}
    assert len(meta['documents']) == len(docs) and set(records) == {d['id'] for d in docs}
    assert sha(run / 'snapshots/week07/data/test-manifest.json') == sha(ROOT / 'week07/data/test-manifest.json')
    rows = []
    for d in docs:
        rec = records[d['id']]
        assert rec['input_sha256'] == d['sha256']
        for f in rec['output_files']:
            assert sha(run / f['file']) == f['sha256'], f['file']
        ref = read(ROOT / d['reference'])
        success = rec['status'] == 'completed'
        raw = run / d['id'] / 'document.json'
        if success:
            assert any(f['file'] == str(raw.relative_to(run)) for f in rec['output_files'])
        data = read(raw) if success else {}
        blocks = pdf.extract(data) if success else []
        pred = ''.join(blocks)
        positions = [pdf.norm(pred).find(pdf.norm(m)) for m in ref['reading_order']]
        pairs = [positions[i] >= 0 and positions[j] > positions[i] for i in range(len(positions)) for j in range(i + 1, len(positions))]
        rows.append({**{k: d[k] for k in ['id', 'type', 'layout', 'scan_quality']},
                     'success': success, 'score': pdf.similarity(''.join(ref['blocks']), pred) if success else 0,
                     'reading_order': sum(pairs) / len(pairs) if pairs else None,
                     'table_exact': pdf.table_exact(data, ref) if success and ref['table_grid'] else False if ref['table_grid'] else None,
                     'seconds': rec['elapsed_seconds'], 'prediction': pred, 'reference': ''.join(ref['blocks']),
                     'raw': str(raw.relative_to(ROOT)), 'input': d['path'], 'reference_file': d['reference']})
    return rows, meta
