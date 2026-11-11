"""CPU LoRA SFT: frozen data -> base evaluation -> train -> reload -> evaluate.
Only answer tokens contribute to loss. No Week07 inputs are read.
"""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import random
import resource
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def verify_data():
    frozen = json.loads((ROOT / 'week08/data/freeze.json').read_text())
    for name, item in frozen['files'].items():
        if digest(ROOT / name) != item['sha256']:
            raise ValueError(f'Data hash mismatch: {name}')
    if digest(ROOT / 'week08/scripts/prepare_data.py') != frozen['generator_sha256']:
        raise ValueError('Generator changed after freezing')
    return frozen


def score(rows):
    counts = dict(exact=0, json_valid=0, total_correct=0, currency_correct=0)
    for row in rows:
        try:
            obj = json.loads(row['prediction'].strip())
            valid = isinstance(obj, dict)
        except (ValueError, TypeError):
            obj, valid = {}, False
        row['json_valid'] = valid
        row['total_correct'] = valid and obj.get('total') == row['answer']['total']
        row['currency_correct'] = valid and obj.get('currency') == row['answer']['currency']
        row['exact'] = valid and obj == row['answer']
        for k in counts:
            counts[k] += int(row[k])
    return {k + '_rate': v / len(rows) for k, v in counts.items()} | {'n': len(rows)}


def run(args):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    from peft import LoraConfig, PeftModel, TaskType, get_peft_model

    config_path = (ROOT / args.config).resolve()
    cfg = json.loads(config_path.read_text())
    frozen = verify_data()
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    torch.set_num_threads(cfg['threads'])
    torch.use_deterministic_algorithms(True)
    set_seed(cfg['seed'])
    name = cfg['name'] + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = ROOT / 'week08/runs' / name
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    save(out / 'config.json', cfg)
    snap = out / 'snapshots'
    snap.mkdir()
    for path in [Path(__file__), ROOT / 'week08/scripts/prepare_data.py', ROOT / 'week08/data/freeze.json', ROOT / 'week08/post-training-plan.md']:
        shutil.copy2(path, snap / path.name)
    metadata = {'status': 'started', 'started_utc': datetime.now(timezone.utc).isoformat(),
                'git_base': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                'git_status': subprocess.check_output(['git','status','--short'], cwd=ROOT, text=True),
                'python': sys.version, 'platform': platform.platform(),
                'packages': {p: importlib.metadata.version(p) for p in ['torch','transformers','peft','accelerate','huggingface-hub','tokenizers','safetensors']},
                'source_sha256': digest(Path(__file__)), 'freeze_sha256': digest(ROOT/'week08/data/freeze.json'),
                'config_sha256': digest(config_path), 'model_id': cfg['model_id'], 'revision': cfg['revision'],
                'cuda_available': torch.cuda.is_available(), 'gpu_hours': 0, 'paid_cost_cny': 0}
    save(out / 'metadata.json', metadata)
    print('OUTPUT', out.relative_to(ROOT), flush=True)
    try:
        def load(split):
            return [json.loads(line) for line in (ROOT/f'week08/data/{split}.jsonl').read_text().splitlines()]
        train, val = load('train'), load('validation')
        tokenizer = AutoTokenizer.from_pretrained(cfg['model_id'], revision=cfg['revision'], cache_dir=str(ROOT/cfg['cache_dir']), local_files_only=True)
        tokenizer.pad_token = tokenizer.eos_token
        base = AutoModelForCausalLM.from_pretrained(cfg['model_id'], revision=cfg['revision'], cache_dir=str(ROOT/cfg['cache_dir']), local_files_only=True, dtype=torch.float32, attn_implementation='eager')
        base.config.use_cache = False
        def prompt(row):
            return frozen['prompt'].format(text=row['text'])
        def encode(row):
            p = tokenizer.encode(prompt(row), add_special_tokens=False)
            a = tokenizer.encode(json.dumps(row['answer'], separators=(',', ':')), add_special_tokens=False) + [tokenizer.eos_token_id]
            ids = p + a
            if len(ids) > cfg['max_length']:
                raise ValueError('Sequence exceeds planned length; refusing silent truncation')
            return ids, [-100]*len(p)+a
        encoded_train, encoded_val = [encode(x) for x in train], [encode(x) for x in val]
        def batch(items):
            width = max(len(x[0]) for x in items)
            ids = [x[0]+[tokenizer.pad_token_id]*(width-len(x[0])) for x in items]
            labels = [x[1]+[-100]*(width-len(x[1])) for x in items]
            mask = [[1]*len(x[0])+[0]*(width-len(x[0])) for x in items]
            return {k: torch.tensor(v) for k,v in [('input_ids',ids),('labels',labels),('attention_mask',mask)]}
        def nll(model, items):
            model.eval()
            total, tokens = 0., 0
            with torch.no_grad():
                for i in range(0,len(items),cfg['batch_size']):
                    b = batch(items[i:i+cfg['batch_size']])
                    n = int((b['labels'][:,1:] != -100).sum())
                    total += float(model(**b).loss)*n
                    tokens += n
            return total/tokens
        def evaluate(model, tag):
            t = time.monotonic()
            model.eval()
            rows = []
            with torch.no_grad():
                for row in val:
                    inputs = tokenizer(prompt(row), return_tensors='pt', add_special_tokens=False)
                    seq = model.generate(**inputs, do_sample=False, max_new_tokens=cfg['max_new_tokens'], pad_token_id=tokenizer.pad_token_id, eos_token_id=tokenizer.eos_token_id, use_cache=True)
                    pred = tokenizer.decode(seq[0,inputs['input_ids'].shape[1]:], skip_special_tokens=True)
                    rows.append({'id':row['id'], 'prompt':prompt(row), 'answer':row['answer'], 'prediction':pred})
            metrics = score(rows) | {'answer_nll':nll(model,encoded_val), 'seconds':time.monotonic()-t}
            save(out/f'{tag}-predictions.json',rows)
            save(out/f'{tag}-metrics.json',metrics)
            print(tag, json.dumps(metrics), flush=True)
            return rows, metrics
        baseline_rows, baseline = evaluate(base,'baseline')
        # Baseline is on disk before any adapter exists or optimizer update runs.
        metadata['baseline_saved_before_training'] = True
        metadata['baseline_sha256'] = digest(out/'baseline-predictions.json')
        set_seed(cfg['seed'])
        model = get_peft_model(base, LoraConfig(task_type=TaskType.CAUSAL_LM, r=cfg['r'], lora_alpha=cfg['lora_alpha'], lora_dropout=cfg['lora_dropout'], target_modules=cfg['target_modules'], bias='none', revision=cfg['revision']))
        trainable = {n:p for n,p in model.named_parameters() if p.requires_grad}
        assert trainable and all('lora_' in n for n in trainable)
        def base_hash():
            h=hashlib.sha256()
            for n,p in model.named_parameters():
                if 'lora_' not in n:
                    h.update(n.encode()); h.update(p.detach().contiguous().numpy().tobytes())
            return h.hexdigest()
        frozen_weights = base_hash()
        metadata.update(trainable_parameters=sum(p.numel() for p in trainable.values()), total_parameters=sum(p.numel() for p in model.parameters()), trainable_names=list(trainable), max_sequence_length=max(len(x[0]) for x in encoded_train+encoded_val), frozen_base_before_sha256=frozen_weights)
        save(out/'metadata.json',metadata)
        optimizer = torch.optim.AdamW(trainable.values(), lr=cfg['learning_rate'], weight_decay=cfg['weight_decay'])
        rng = random.Random(cfg['seed'])
        order, pos = [], 0
        def next_batch():
            nonlocal order,pos
            if pos+cfg['batch_size']>len(order):
                order=list(range(len(train))); rng.shuffle(order); pos=0
            inds=order[pos:pos+cfg['batch_size']]; pos+=cfg['batch_size']
            return batch([encoded_train[i] for i in inds])
        train_start = time.monotonic()
        with (out/'training.jsonl').open('w') as log:
            for step in range(1,cfg['max_steps']+1):
                if time.monotonic()-train_start>cfg['training_timeout_seconds']:
                    raise TimeoutError('Training budget exhausted')
                model.train(); optimizer.zero_grad(set_to_none=True)
                losses=[]
                for _ in range(cfg['gradient_accumulation_steps']):
                    loss=model(**next_batch()).loss
                    if not torch.isfinite(loss):
                        raise FloatingPointError('Non-finite loss')
                    (loss/cfg['gradient_accumulation_steps']).backward()
                    losses.append(float(loss.detach()))
                norm = float(torch.nn.utils.clip_grad_norm_(trainable.values(),1.0))
                optimizer.step()
                record={'step':step,'train_loss':sum(losses)/len(losses),'gradient_norm':norm,'elapsed_seconds':time.monotonic()-train_start}
                if step%cfg['eval_every']==0:
                    record['validation_answer_nll']=nll(model,encoded_val)
                    print('STEP',json.dumps(record),flush=True)
                log.write(json.dumps(record)+'\n'); log.flush()
        metadata['training_seconds']=time.monotonic()-train_start
        metadata['frozen_base_after_sha256']=base_hash()
        assert metadata['frozen_base_after_sha256']==frozen_weights, 'Base weights changed'
        model.save_pretrained(out/'adapter',safe_serialization=True)
        after_rows, after=evaluate(model,'after')
        # Verify persisted artifact by reloading from disk onto the same frozen base.
        plain=model.unload()
        reloaded=PeftModel.from_pretrained(plain,out/'adapter',is_trainable=False)
        reload_rows,reload_metrics=evaluate(reloaded,'reloaded')
        assert [r['prediction'] for r in after_rows]==[r['prediction'] for r in reload_rows]
        metadata['reload_predictions_equal']=True
        metadata['status']='complete'
        metadata['adapter_sha256']=digest(out/'adapter/adapter_model.safetensors')
        save(out/'comparison.json',{'baseline':baseline,'after':after,'delta_exact_rate':after['exact_rate']-baseline['exact_rate'], 'delta_answer_nll':after['answer_nll']-baseline['answer_nll']})
    except Exception:
        metadata['status']='failed'
        save(out/'failure.json',{'traceback':traceback.format_exc()})
        raise
    finally:
        metadata['total_seconds']=time.monotonic()-started
        metadata['peak_rss_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        save(out/'metadata.json',metadata)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default='week08/configs/run-a.json')
    parser.add_argument('--verify-only',action='store_true',help='Verify frozen data hashes without loading model')
    args=parser.parse_args()
    if args.verify_only:
        verify_data(); print('Frozen data and generator SHA-256 verified.'); return
    run(args)

if __name__=='__main__':
    main()
