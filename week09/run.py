"""Run the frozen A/B comparison and an explicitly labelled failure drill."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-drill', action='store_true', help='Run only A/B')
    args = parser.parse_args()
    evidence = ROOT / 'week09/evidence'
    evidence.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    jobs = [('a', 'week09/configs/run-a.json', 0), ('b', 'week09/configs/run-b.json', 0)]
    if not args.skip_drill:
        jobs.append(('failure-drill', 'week09/configs/run-a.json', 2))
    records = []
    for label, cfg, fail in jobs:
        before = set((ROOT / 'week09/runs').glob('*'))
        cmd = [sys.executable, 'week08/train.py', '--config', cfg,
               '--output-root', 'week09/runs', '--wandb-mode', 'offline',
               '--fail-at-step', str(fail)]
        logfile = evidence / f'{stamp}-{label}.log'
        print('RUN', label, 'LOG', logfile.relative_to(ROOT), flush=True)
        with logfile.open('w') as log:
            result = subprocess.run(cmd, cwd=ROOT, env=dict(os.environ, HF_HUB_OFFLINE='1'),
                                    stdout=log, stderr=subprocess.STDOUT)
        created = sorted(set((ROOT / 'week09/runs').glob('*')) - before)
        records.append({'label': label, 'command': cmd[1:], 'exit_code': result.returncode,
                        'log': str(logfile.relative_to(ROOT)),
                        'directories': [str(p.relative_to(ROOT)) for p in created]})
        (evidence / f'suite-{stamp}.json').write_text(json.dumps(records, indent=2) + '\n')
        print(label, 'EXIT', result.returncode, 'OUTPUT', records[-1]['directories'], flush=True)
        if (not fail and result.returncode != 0) or (fail and result.returncode == 0):
            raise SystemExit('Unexpected exit status; inspect retained log before retrying')


if __name__ == '__main__':
    main()
