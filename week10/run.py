"""Run one immutable Week10 suite, preserving subprocess logs and failures."""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'week10/scripts'))
from common import verify, save, sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf-run', type=Path, help='Reuse a completed Week10 no-OCR run; otherwise run it now')
    ap.add_argument('--verify-only', action='store_true', help='Authenticate protocol and frozen inputs only')
    args = ap.parse_args()
    verify()
    if args.verify_only:
        print('Protocol, input freezes, adapters and single-variable configurations verified.'); return
    out = ROOT / 'week10/runs' / ('suite-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    out.mkdir(parents=True)
    state = {'status': 'running', 'protocol_sha256': sha(ROOT / 'week10/configs/protocol.json'), 'commands': [], 'text': {}}
    env = os.environ | {'HF_HUB_OFFLINE': '1'}
    def execute(label, command, timeout, allowed=(0,)):
        rec = {'label': label, 'command': command, 'log': str((out / f'{label}.log').relative_to(ROOT))}
        state['commands'].append(rec)
        save(out / 'suite.json', state)
        with (out / f'{label}.log').open('w') as log:
            try:
                rec['exit_code'] = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout).returncode
            except subprocess.TimeoutExpired:
                rec['exit_code'] = 124
        save(out / 'suite.json', state)
        if rec['exit_code'] not in allowed:
            raise RuntimeError(f'{label} exited {rec["exit_code"]}; see {rec["log"]}')
    try:
        if args.pdf_run:
            pdf_run = args.pdf_run.resolve()
        else:
            before = set((ROOT / 'week10/runs/pdf').glob('*')) if (ROOT / 'week10/runs/pdf').exists() else set()
            execute('pdf-no-ocr', [str(ROOT / '.venv-week06/bin/python'), 'week06/scripts/run_pipeline.py', '--config', 'week10/configs/pdf-no-ocr.json'], 24 * 600 + 120, allowed=(0,1))
            created = set((ROOT / 'week10/runs/pdf').glob('*')) - before
            assert len(created) == 1
            pdf_run = created.pop()
        pdf_meta = json.loads((pdf_run / 'run-metadata.json').read_text())
        if pdf_meta['status'] not in ['completed','failed'] or len(pdf_meta['documents']) != 24:
            raise ValueError('PDF run must have finished all 24 pages, retaining failed pages')
        state['pdf_no_ocr'] = str(pdf_run.relative_to(ROOT))
        for name in ['base', 'run-a', 'run-b']:
            folder = out / name
            execute(name, [str(ROOT / '.venv-week08/bin/python'), 'week10/scripts/evaluate_text.py', '--model', name, '--output', str(folder)], 600)
            state['text'][name] = str(folder.relative_to(ROOT))
        state['status'] = 'complete'
    except Exception as e:
        state['status'] = 'failed'
        state['error'] = str(e)
        raise
    finally:
        save(out / 'suite.json', state)
        print(out.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
