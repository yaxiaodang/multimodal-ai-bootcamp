"""Authenticate receipts and independently recompute metrics; no model or network."""
from common import ROOT, read, sha, verify, pdf_rows, score, aggregate
import math


def equal(a, b):
    # Python 3.12+ changed sum(float) accumulation; allow rounding only.
    if isinstance(a, float) and isinstance(b, (int,float)):
        return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equal(v,b[k]) for k,v in a.items())
    return a == b


def main():
    p, docs = verify()
    manifest = read(ROOT / 'week10/evidence/manifest.json')
    for path, expected in manifest['files'].items():
        assert sha(ROOT / path) == expected, path
    summary = read(ROOT / 'week10/reports/comparison.json')
    suite = read(ROOT / manifest['suite'])
    assert suite['status'] == 'complete'
    checks = {}
    for label, path in [('pdf-baseline',p['pdf_baseline']),('pdf-no-ocr',suite['pdf_no_ocr'])]:
        rows, _ = pdf_rows(ROOT / path,docs)
        assert rows == summary['results'][label]['documents']
        assert equal(aggregate(rows), summary['results'][label]['overall'])
        checks[label] = {'n':len(rows),'score':aggregate(rows)['score']}
    source = [__import__('json').loads(x) for x in (ROOT / p['text_split']).read_text().splitlines()]
    for label,folder in suite['text'].items():
        rows = read(ROOT / folder / 'predictions.json')
        assert [(r['id'],r['text'],r['answer']) for r in rows] == [(r['id'],r['text'],r['answer']) for r in source]
        metrics = score(rows)
        assert rows == summary['results'][label]['documents']
        assert equal(metrics | aggregate(rows), summary['results'][label]['overall'])
        checks[label] = metrics
    errors = read(ROOT / 'week10/reports/error-taxonomy.json')
    assert len({e['case_id'] for e in errors}) == len(errors)
    assert len(errors) >= 20
    assert all(e['review_status'] == 'pending_user' for e in errors)
    result = {'passed':True,'checks':checks,'authenticated_files':len(manifest['files']),
              'error_cases':len(errors),'manual_review':'pending_user','cloud_report':'not_created'}
    from common import save
    save(ROOT / 'week10/evidence/verification.json', result)
    print(__import__('json').dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
