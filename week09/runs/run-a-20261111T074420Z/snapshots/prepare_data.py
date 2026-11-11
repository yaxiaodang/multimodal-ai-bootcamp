"""Create and freeze fictional teaching data; never reads Week07."""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'week08/data'
PROMPT = 'Extract the final total and currency. Return only JSON with string keys total and currency.\nDocument:\n{text}\nAnswer:\n'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    if (DATA / 'freeze.json').exists():
        raise SystemExit('Data already frozen; refusing to overwrite v1.')
    rng = random.Random(20261111)
    templates = [
        'Invoice {id}\nCurrency: {currency}\nSubtotal: {subtotal}\nTax: {tax}\nTotal: {total}',
        'Receipt {id} | Subtotal {subtotal} | Tax {tax} | Total {total} {currency}',
        'BILL {id}\nTax = {tax}\nFinal total = {total} {currency}\nSubtotal = {subtotal}',
    ]
    manifest = {'version': '1.0', 'seed': 20261111, 'files': {}, 'prompt': PROMPT,
                'generator_sha256': sha(Path(__file__))}
    seen = set()
    for split, count, start in [('train', 96, 1000), ('validation', 12, 2000), ('reserved-test', 12, 3000)]:
        rows = []
        for i in range(count):
            sub, tax = rng.randint(100, 80000), rng.randint(0, 3000)
            values = dict(id=f'F{start+i}', currency=['USD', 'EUR', 'GBP'][i % 3],
                          subtotal=f'{sub/100:.2f}', tax=f'{tax/100:.2f}', total=f'{(sub+tax)/100:.2f}')
            text = templates[i % 3].format(**values)
            assert text not in seen
            seen.add(text)
            rows.append({'id': values['id'], 'split': split, 'template': i % 3, 'text': text,
                         'answer': {'total': values['total'], 'currency': values['currency']}})
        path = DATA / f'{split}.jsonl'
        path.write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in rows))
        manifest['files'][str(path.relative_to(ROOT))] = {'sha256': sha(path), 'count': count}
    (DATA / 'freeze.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('Frozen: 96 train, 12 validation, 12 reserved-test; exact text duplicates=0.')

if __name__ == '__main__':
    main()
