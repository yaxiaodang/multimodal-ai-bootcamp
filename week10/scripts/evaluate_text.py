"""Evaluate one fixed base/Week09 adapter on reserved-test; never train."""
import argparse
import importlib.metadata
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from common import ROOT, read, save, sha, verify, score, aggregate, slices


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--model', choices=['base', 'run-a', 'run-b'], required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    p, _ = verify()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    meta = {'status': 'started', 'model': args.model, 'started_utc': datetime.now(timezone.utc).isoformat(),
            'protocol_sha256': sha(ROOT / 'week10/configs/protocol.json'),
            'source_sha256': {str(Path(f).relative_to(ROOT)): sha(f) for f in [__file__, Path(__file__).with_name('common.py')]},
            'git_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
            'python': sys.version, 'platform': platform.platform(), 'gpu_hours': 0, 'paid_cost_cny': 0,
            'training': False, 'model_source': p['text_runs'][args.model],
            'wandb_project': 'multimodal-ai-bootcamp-week09', 'evaluation_wandb_run': None,
            'cloud_report_url': None}
    save(out / 'metadata.json', meta)
    try:
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, set_seed
        from peft import PeftModel
        torch.set_num_threads(p['threads'])
        torch.use_deterministic_algorithms(True)
        set_seed(p['seed'])
        cfg = read(ROOT / p['text_runs']['run-a'] / 'config.json')
        meta['packages'] = {n: importlib.metadata.version(n) for n in ['torch','transformers','peft','tokenizers','safetensors']}
        meta['model_id'], meta['revision'] = cfg['model_id'], cfg['revision']
        tokenizer = AutoTokenizer.from_pretrained(cfg['model_id'], revision=cfg['revision'], cache_dir=str(ROOT / cfg['cache_dir']), local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(cfg['model_id'], revision=cfg['revision'], cache_dir=str(ROOT / cfg['cache_dir']), local_files_only=True, dtype=torch.float32, attn_implementation='eager')
        if args.model != 'base':
            source = ROOT / p['text_runs'][args.model]
            model = PeftModel.from_pretrained(model, source / 'adapter', is_trainable=False)
            meta['training_wandb_identity'] = read(source / 'wandb-identity.json')
            meta['training_artifacts'] = str((source / 'artifact-manifest.json').relative_to(ROOT))
        model.eval()
        meta['load_seconds'] = time.monotonic() - started
        frozen = read(ROOT / 'week08/data/freeze.json')
        rows = []
        for line in (ROOT / p['text_split']).read_text().splitlines():
            row = __import__('json').loads(line)
            prompt = frozen['prompt'].format(text=row['text'])
            inputs = tokenizer(prompt, return_tensors='pt', add_special_tokens=False)
            tick = time.monotonic()
            with torch.inference_mode():
                seq = model.generate(**inputs, **p['generation'], pad_token_id=tokenizer.eos_token_id, eos_token_id=tokenizer.eos_token_id, use_cache=True)
            pred = tokenizer.decode(seq[0, inputs['input_ids'].shape[1]:], skip_special_tokens=True)
            rows.append({**row, 'prompt': prompt, 'prediction': pred, 'seconds': time.monotonic() - tick,
                         'input_tokens': inputs['input_ids'].shape[1], 'output_tokens': seq.shape[1] - inputs['input_ids'].shape[1]})
        metrics = score(rows)
        save(out / 'predictions.json', rows)
        save(out / 'metrics.json', {'overall': metrics | aggregate(rows), 'slices': slices(rows, ['template'])})
        meta['status'] = 'complete'
        meta['predictions_sha256'] = sha(out / 'predictions.json')
        print(args.model, metrics, flush=True)
    except Exception:
        import traceback
        meta['status'] = 'failed'
        meta['traceback'] = traceback.format_exc()
        raise
    finally:
        meta['total_seconds'] = time.monotonic() - started
        meta['peak_rss_mib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        save(out / 'metadata.json', meta)


if __name__ == '__main__':
    main()
