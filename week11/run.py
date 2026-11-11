"""Week11 entry: verify fixed protocol, train ranks 4/8, check mechanisms, report."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from week08.train import digest, save, verify_data

INPUTS=['week11/experiment-plan.md','week11/run.py','week11/scripts/check_mechanism.py','week11/configs/rank-4.json','week11/configs/rank-8.json','week08/train.py','week08/data/freeze.json','week08/data/train.jsonl','week08/data/validation.jsonl','week08/data/reserved-test.jsonl']


def preflight():
    verify_data()
    a,b=[json.loads((ROOT/f'week11/configs/rank-{r}.json').read_text()) for r in [4,8]]
    diff={k:[a[k],b[k]] for k in a if a[k]!=b[k]}
    if set(diff)!={'r','name'} or diff['r']!=[4,8]:
        raise ValueError(f'Expected only r + identity name to differ: {diff}')
    if a['max_steps']!=60 or a['lora_alpha']!=16 or a['seed']!=42:
        raise ValueError('Preregistered constants changed')
    return {'config_diff':diff,'input_sha256':{p:digest(ROOT/p) for p in INPUTS}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only',action='store_true',help='Check frozen input/config hashes without loading models')
    parser.add_argument('--check-archive',action='store_true',help='Verify archived files and recalculate scores, no model/network')
    args=parser.parse_args()
    if args.check_archive:
        subprocess.run([sys.executable,str(ROOT/'week11/scripts/verify.py')],check=True,cwd=ROOT)
        return
    checked=preflight()
    if args.verify_only:
        print(json.dumps(checked,indent=2)); return
    # Check plan and executable inputs were committed BEFORE this new run.
    for p in INPUTS:
        committed=subprocess.check_output(['git','show',f'HEAD:{p}'],cwd=ROOT)
        if hashlib.sha256(committed).hexdigest()!=checked['input_sha256'][p]:
            raise ValueError(f'Uncommitted protocol/source change: {p}; commit before running')
    suite=ROOT/'week11/runs'/('suite-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    suite.mkdir(parents=True,exist_ok=False)
    snap=suite/'snapshots'
    for p in INPUTS:
        dest=snap/p
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/p,dest)
    record={'status':'started','started_utc':datetime.now(timezone.utc).isoformat(),'preregistered_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'preflight':checked,'runs':{},'commands':[]}
    save(suite/'suite.json',record)
    env=dict(os.environ,HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')

    def execute(cmd,log,timeout):
        item={'argv':cmd,'log':str(log.relative_to(ROOT)),'timeout_seconds':timeout}
        record['commands'].append(item)
        save(suite/'suite.json',record)
        with log.open('w') as stream:
            try:
                proc=subprocess.run(cmd,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout)
                item['exit_code']=proc.returncode
                if proc.returncode:
                    raise RuntimeError(f'Command failed ({proc.returncode}); see {log.relative_to(ROOT)}')
            except subprocess.TimeoutExpired:
                item['status']='timeout'
                raise
        save(suite/'suite.json',record)

    try:
        for rank in [4,8]:
            output=suite/f'rank-{rank}'
            cmd=[sys.executable,'week08/train.py','--config',f'week11/configs/rank-{rank}.json','--output-root',str(output.relative_to(ROOT))]
            print(f'Train rank {rank}; log: {suite.relative_to(ROOT)}/rank-{rank}-train.log',flush=True)
            execute(cmd,suite/f'rank-{rank}-train.log',1200)
            folders=list(output.glob('rank-*'))
            if len(folders)!=1: raise RuntimeError('Ambiguous training output')
            record['runs'][str(rank)]=str(folders[0].relative_to(ROOT))
            print(f'Check real adapter rank {rank}',flush=True)
            execute([sys.executable,'week11/scripts/check_mechanism.py','--run',record['runs'][str(rank)]],suite/f'rank-{rank}-mechanism.log',300)
        record['status']='complete'
    except Exception as exc:
        record['status']='failed'
        record['error']=repr(exc)
        raise
    finally:
        record['finished_utc']=datetime.now(timezone.utc).isoformat()
        save(suite/'suite.json',record)
        print('SUITE',suite.relative_to(ROOT),flush=True)
    subprocess.run([sys.executable,'week11/scripts/build_report.py','--suite',str((suite/'suite.json').relative_to(ROOT))],cwd=ROOT,check=True)


if __name__=='__main__':
    main()
