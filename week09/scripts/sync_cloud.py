"""Preview or sync the recorded offline runs and export real cloud identifiers."""
import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entity', required=True, help='Actual W&B account/team slug')
    parser.add_argument('--sync', action='store_true', help='Upload runs; default only prints commands')
    parser.add_argument('--report-url', help='Existing published W&B Report URL to record')
    args = parser.parse_args()
    if args.report_url:
        url = urlparse(args.report_url)
        if url.scheme != 'https' or url.hostname != 'wandb.ai':
            parser.error('--report-url must be an https://wandb.ai/ URL')
    env = dict(os.environ, WANDB_CACHE_DIR=str(ROOT / '.cache-week09/artifacts'),
               WANDB_DATA_DIR=str(ROOT / '.cache-week09/staging'),
               WANDB_CONFIG_DIR=str(ROOT / 'week09/.wandb-config'))
    identity_paths = sorted((ROOT / 'week09/runs').glob('*/wandb-identity.json'))
    identities = [json.loads(p.read_text()) for p in identity_paths]
    output = {'entity': args.entity, 'report_url': args.report_url, 'runs': []}
    for identity, local_path in zip(identities, identity_paths):
        cmd = [sys.executable, '-m', 'wandb', 'sync', '--entity', args.entity,
               '--project', identity['project'], str(ROOT / identity['offline_directory'])]
        print(shlex.join(cmd), flush=True)
        if args.sync:
            metadata = json.loads((local_path.parent / 'metadata.json').read_text())
            if metadata['status'] not in {'complete', 'failed'}:
                raise SystemExit('Run is still in progress; wait for completion before sync.')
            if not (ROOT / identity['offline_directory']).exists():
                raise SystemExit('Native spool missing. On a fresh clone rerun week09/run.py before sync.')
            subprocess.run(cmd, cwd=ROOT, env=env, check=True)
    if args.sync:
        import wandb
        api = wandb.Api()
        for identity, local_path in zip(identities, identity_paths):
            run = api.run(f"{args.entity}/{identity['project']}/{identity['run_id']}")
            artifacts = [{'name': a.name, 'digest': a.digest, 'type': a.type}
                         for a in run.logged_artifacts()]
            expected = json.loads((local_path.parent / 'artifact-manifest.json').read_text())
            for artifact in expected:
                matches = [a for a in artifacts if a['name'].rsplit(':', 1)[0] == artifact['name']
                           and a['digest'] == artifact['digest']]
                if not matches:
                    raise SystemExit(f"Cloud artifact missing or digest differs: {artifact['name']}")
            output['runs'].append({'run_id': run.id, 'url': run.url, 'state': run.state,
                                   'artifact_digests_verified': True, 'artifacts': artifacts})
        path = ROOT / 'week09/reports/cloud-links.json'
        path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n')
        print('Saved', path.relative_to(ROOT))
    else:
        print('Preview only; add --sync after login. No cloud data changed.')


if __name__ == '__main__':
    main()
