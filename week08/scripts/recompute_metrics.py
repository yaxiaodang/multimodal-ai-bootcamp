"""Recompute task scores from raw predictions, with no model execution."""
import argparse
import importlib.util
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('train',root/'week08/train.py')
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--run',required=True,help='Run directory, relative to repository root or absolute')
args=parser.parse_args()
run=root/args.run
for tag in ['baseline','after','reloaded']:
    path=run/f'{tag}-predictions.json'
    if not path.exists():
        raise SystemExit(f'Missing raw output: {path}')
    rows=json.loads(path.read_text())
    scores=module.score(rows)
    original=json.loads((run/f'{tag}-metrics.json').read_text())
    assert all(original[k]==v for k,v in scores.items()),f'Metrics mismatch: {tag}'
    print(tag,json.dumps(scores))
print('All task metrics match saved raw predictions. NLL requires a model and is not recomputed here.')
