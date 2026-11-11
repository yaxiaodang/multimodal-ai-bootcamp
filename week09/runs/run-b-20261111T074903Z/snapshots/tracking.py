"""Explicit W&B logging plus portable JSON exports. No credentials are read/exported."""
import json
import os
import time
from pathlib import Path

import psutil
import wandb

from week08.train import ROOT, digest, save


class Tracker:
    def __init__(self, out, cfg, metadata, args):
        self.out = out
        self.process = psutil.Process()
        self.process.cpu_percent()
        self.started = time.monotonic()
        self.artifacts = []
        self.export_summary = {}
        # Keep the spool and artifact cache until wandb sync completes.
        os.environ['WANDB_CACHE_DIR'] = str(ROOT / '.cache-week09/artifacts')
        os.environ['WANDB_DATA_DIR'] = str(ROOT / '.cache-week09/staging')
        os.environ['WANDB_CONFIG_DIR'] = str(ROOT / 'week09/.wandb-config')
        spool = ROOT / 'week09/wandb'
        spool.mkdir(parents=True, exist_ok=True)
        config = dict(cfg, git_commit=metadata['git_base'],
                      data_version='week08-synthetic-invoices-v1.0',
                      data_freeze_sha256=metadata['freeze_sha256'],
                      training_source_sha256=metadata['source_sha256'],
                      tracking_source_sha256=digest(Path(__file__)),
                      evaluation_split='validation', fail_at_step=args.fail_at_step)
        self.run = wandb.init(project=args.wandb_project, entity=args.wandb_entity,
                              name=out.name, group='lr-only-seed42',
                              tags=['cpu', 'lora', 'synthetic', 'week09'] +
                                   (['intentional-failure'] if args.fail_at_step else []),
                              config=config, mode=args.wandb_mode, dir=str(spool),
                              settings=wandb.Settings(disable_git=True, console='off',
                                                      x_stats_sampling_interval=2.0))
        self.run.define_metric('train/step')
        self.run.define_metric('train/*', step_metric='train/step')
        self.run.define_metric('validation/*', step_metric='train/step')
        save(out / 'tracking-config.json', config)
        self.identity = {'project': args.wandb_project, 'entity': args.wandb_entity,
                         'run_id': self.run.id, 'mode': args.wandb_mode,
                         'url': self.run.url if args.wandb_mode == 'online' else None,
                         'offline_directory': str(Path(self.run.dir).parent.relative_to(ROOT)),
                         'cloud_synced': args.wandb_mode == 'online',
                         'report_url': None}
        save(out / 'wandb-identity.json', self.identity)
        snap = out / 'snapshots'
        import shutil
        shutil.copy2(__file__, snap / 'tracking.py')
        self.artifact('invoices-v1', 'dataset', [ROOT / 'week08/data/train.jsonl',
                      ROOT / 'week08/data/validation.jsonl', ROOT / 'week08/data/freeze.json',
                      ROOT / 'week08/dataset-card.md'], role='input')
        self.artifact('training-source', 'code', list(snap.iterdir()) +
                      [out / 'config.json', out / 'tracking-config.json'], role='source')

    def log(self, record):
        record = dict(record, **{'resource/process_rss_mib': self.process.memory_info().rss / 2**20,
                                'resource/process_cpu_percent': self.process.cpu_percent(),
                                'resource/host_memory_percent': psutil.virtual_memory().percent,
                                'resource/elapsed_seconds': time.monotonic() - self.started})
        with (self.out / 'history.jsonl').open('a') as f:
            f.write(json.dumps(record) + '\n')
        self.run.log(record)
        self.export_summary.update(record)

    def training(self, row, lr):
        values = {'train/step': row['step'], 'train/loss': row['train_loss'],
                  'train/learning_rate': lr, 'train/gradient_norm': row['gradient_norm'],
                  'train/elapsed_seconds': row['elapsed_seconds']}
        if 'validation_answer_nll' in row:
            values['validation/answer_nll'] = row['validation_answer_nll']
        self.log(values)

    def evaluation(self, tag, metrics, rows):
        self.log({f'{tag}/{k}': v for k, v in metrics.items()})
        table = wandb.Table(columns=['id', 'expected', 'prediction', 'exact'], data=[
            [r['id'], json.dumps(r['answer']), r['prediction'], r['exact']] for r in rows])
        self.run.log({f'{tag}/predictions': table})

    def artifact(self, name, kind, paths, role):
        artifact = wandb.Artifact(name, type=kind, metadata={
            'role': role, 'git_commit': self.run.config['git_commit'],
            'data_freeze_sha256': self.run.config['data_freeze_sha256'],
            'run_id': self.run.id})
        files = []
        for path in sorted(paths):
            path = Path(path)
            artifact.add_file(str(path), name=str(path.relative_to(ROOT)))
            files.append({'path': str(path.relative_to(ROOT)), 'sha256': digest(path),
                          'bytes': path.stat().st_size})
        self.run.log_artifact(artifact)
        # Offline artifacts have local digests; server :vN exists only after sync.
        self.artifacts.append({'name': name, 'type': kind, 'role': role,
                               'digest': artifact.digest, 'cloud_version': None, 'files': files})
        save(self.out / 'artifact-manifest.json', self.artifacts)

    def finish(self, metadata):
        status = metadata['status']
        summary = {'status': status, 'total_seconds': metadata['total_seconds'],
                                 'training_seconds': metadata.get('training_seconds'),
                                 'peak_rss_mib': metadata['peak_rss_mib'],
                                 'gpu_hours': 0, 'paid_cost_cny': 0,
                                 'adapter_sha256': metadata.get('adapter_sha256'),
                                 'reload_predictions_equal': metadata.get('reload_predictions_equal', False)}
        self.run.summary.update(summary)
        self.export_summary.update(summary)
        self.artifact('results-' + self.run.id, 'evaluation',
                      [p for p in self.out.iterdir() if p.is_file() and p.suffix in {'.json', '.jsonl'}
                       and p.name not in {'artifact-manifest.json', 'wandb-summary.json'}], role='output')
        if (self.out / 'adapter').exists():
            self.artifact('adapter-' + self.run.id, 'model', list((self.out / 'adapter').iterdir()), role='output')
        # SDK summary may contain SummarySubDict for Tables; export our plain values.
        save(self.out / 'wandb-summary.json', self.export_summary)
        self.run.finish(exit_code=0 if status == 'complete' else 1)
