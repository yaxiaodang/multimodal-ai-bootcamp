"""Standard-library archive audit: hashes, preregistration, metrics, claims."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from week08.train import digest, save, score, verify_data


def verify():
    verify_data()
    manifest=json.loads((ROOT/'week11/evidence/manifest.json').read_text())
    for p,sha in manifest['files'].items():
        if digest(ROOT/p)!=sha: raise ValueError(f'Archive hash mismatch: {p}')
    summary=json.loads((ROOT/'week11/reports/comparison.json').read_text())
    suite_path=ROOT/summary['suite']
    suite=json.loads(suite_path.read_text())
    if suite['status']!='complete': raise ValueError('Suite not complete')
    for p,sha in suite['preflight']['input_sha256'].items():
        if digest(ROOT/p)!=sha or digest(suite_path.parent/'snapshots'/p)!=sha:
            raise ValueError(f'Protocol/source changed: {p}')
    config=[]
    counts=[]
    actual={}
    for rank,folder in suite['runs'].items():
        p=ROOT/folder
        config.append(json.loads((p/'config.json').read_text()))
        meta=json.loads((p/'metadata.json').read_text())
        if meta['status']!='complete' or meta['git_base']!=suite['preregistered_commit']:
            raise ValueError('Wrong execution status or registration commit')
        if meta['frozen_base_before_sha256']!=meta['frozen_base_after_sha256']:
            raise ValueError('Base weights changed')
        if not meta['trainable_names'] or not all('lora_A' in n or 'lora_B' in n for n in meta['trainable_names']):
            raise ValueError('Unexpected trainable parameters')
        if meta['adapter_sha256']!=digest(p/'adapter/adapter_model.safetensors'):
            raise ValueError('Adapter changed')
        logs=[json.loads(x) for x in (p/'training.jsonl').read_text().splitlines()]
        if [x['step'] for x in logs]!=list(range(1,61)): raise ValueError('Missing training steps')
        metrics={}
        for tag in ['baseline','after','reloaded','merged']:
            rows=json.loads((p/f'{tag}-predictions.json').read_text())
            computed=score(rows)
            stored=json.loads((p/f'{tag}-metrics.json').read_text())
            if len(rows)!=12 or any(computed[k]!=stored[k] for k in computed):
                raise ValueError(f'Metric mismatch: r{rank}/{tag}')
            metrics[tag]=computed
        a=json.loads((p/'after-predictions.json').read_text())
        for tag in ['reloaded','merged']:
            b=json.loads((p/f'{tag}-predictions.json').read_text())
            if [(x['id'],x['prediction']) for x in a]!=[(x['id'],x['prediction']) for x in b]:
                raise ValueError('Reload/merge mismatch')
        mech=json.loads((p/'mechanism.json').read_text())
        if not mech['passed'] or not mech['merge']['allclose'] or not mech['initialization']['allclose']:
            raise ValueError('Mechanism check failed')
        if len(mech['layers'])!=60 or not all(x['formula_equal'] and x['rank_bound']==int(rank) for x in mech['layers']):
            raise ValueError('Layer formula check failed')
        reported=summary['results'][rank]
        if any(reported['after'][k]!=metrics['after'][k] for k in metrics['after']): raise ValueError('Report differs from raw metrics')
        if reported['trainable_parameters']!=meta['trainable_parameters']: raise ValueError('Parameter count differs')
        counts.append(meta['trainable_parameters'])
        actual[rank]=metrics
    diff={k for k in config[0] if config[0][k]!=config[1][k]}
    if diff!={'name','r'} or counts[1]!=2*counts[0]: raise ValueError('Rank protocol mismatch')
    result={'status':'passed','files_checked':len(manifest['files']),'suite':summary['suite'],'recomputed_metrics':actual,'note':'Automated audit; human review remains pending. Does not re-run model forwards.'}
    save(ROOT/'week11/evidence/verification.json',result)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    verify()
