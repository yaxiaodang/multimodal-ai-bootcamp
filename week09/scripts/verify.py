"""Check raw predictions, single-variable control, artifact files and native W&B records."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from week08.train import digest, score, verify_data


def read(path):
    return json.loads(path.read_text())


def verify():
    verify_data()
    runs = sorted((ROOT / 'week09/runs').glob('*'))
    complete = [p for p in runs if read(p / 'metadata.json')['status'] == 'complete'
                and (p / 'wandb-summary.json').exists()]
    assert len(complete) >= 2, 'Need two completed runs'
    a = next(p for p in complete if read(p / 'config.json')['name'] == 'run-a')
    b = next(p for p in complete if read(p / 'config.json')['name'] == 'run-b')
    ca, cb = read(a / 'config.json'), read(b / 'config.json')
    diff = {k: {'a': ca.get(k), 'b': cb.get(k)} for k in ca.keys() | cb.keys() if ca.get(k) != cb.get(k)}
    assert set(diff) == {'name', 'learning_rate'}, diff
    assert read(a / 'baseline-predictions.json') == read(b / 'baseline-predictions.json')
    evidence = []
    for path in runs:
        metadata = read(path / 'metadata.json')
        row = {'path': str(path.relative_to(ROOT)), 'status': metadata['status']}
        if metadata['status'] == 'complete':
            for tag in ['baseline', 'after', 'reloaded']:
                computed = score(read(path / f'{tag}-predictions.json'))
                saved = read(path / f'{tag}-metrics.json')
                assert all(saved[k] == value for k, value in computed.items())
            assert read(path / 'after-predictions.json') == read(path / 'reloaded-predictions.json')
            assert metadata['frozen_base_before_sha256'] == metadata['frozen_base_after_sha256']
            assert digest(path / 'adapter/adapter_model.safetensors') == metadata['adapter_sha256']
        if (path / 'wandb-identity.json').exists():
            identity = read(path / 'wandb-identity.json')
            export_failed = not (path / 'wandb-summary.json').exists()
            if export_failed:
                assert path.name == 'run-a-20261111T073611Z', 'Unexpected missing summary'
                row['status'] = 'tracking-export-failed'
                row['note'] = 'Training completed, summary export raised SummarySubDict TypeError; suite exit=1 retained'
            else:
                assert read(path / 'wandb-summary.json')['status'] == metadata['status']
            for artifact in read(path / 'artifact-manifest.json'):
                for file in artifact['files']:
                    assert digest(ROOT / file['path']) == file['sha256'], file['path']
            history = [json.loads(s) for s in (path / 'history.jsonl').read_text().splitlines()]
            steps = [s['train/step'] for s in history if 'train/step' in s]
            assert steps == list(range(1, 61 if metadata['status'] == 'complete' else 3))
            assert all('resource/process_rss_mib' in r for r in history)
            # Decode native SDK spool; JSON exports alone do not prove SDK logging.
            from native_records import records
            from wandb.proto import wandb_internal_pb2
            spool = ROOT / identity['offline_directory'] / f"run-{identity['run_id']}.wandb"
            counts = Counter()
            native_steps = []
            native_exit = None
            for data in records(spool):
                record = wandb_internal_pb2.Record()
                record.ParseFromString(data)
                kind = record.WhichOneof('record_type')
                counts[kind] += 1
                if kind == 'exit':
                    native_exit = record.exit.exit_code
                if kind == 'history':
                    for item in record.history.item:
                        key = '.'.join(item.nested_key) if item.nested_key else item.key
                        if key == 'train/step':
                            native_steps.append(json.loads(item.value_json))
            assert counts['stats'] > 0, 'No SDK system metrics captured'
            assert counts['artifact'] >= (4 if metadata['status'] == 'complete' else 3)
            assert native_exit == (0 if metadata['status'] == 'complete' and not export_failed else 1)
            assert native_steps[:len(steps)] == steps
            row.update(run_id=identity['run_id'], native_records=dict(counts), native_exit=native_exit,
                       exported_training_steps=len(steps), artifact_hashes_verified=True)
        else:
            assert metadata['status'] == 'failed' and (path / 'failure.json').exists()
            row['note'] = 'SDK startup failed before run ID; retained for audit'
        evidence.append(row)
    result = {'status': 'passed', 'config_diff': diff, 'same_baseline_predictions': True,
              'checks': evidence}
    (ROOT / 'week09/evidence/verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    verify()
