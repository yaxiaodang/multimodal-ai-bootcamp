"""Load a real adapter and check initialization, delta formula and merged inference."""
import argparse
import gc
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from week08.train import digest, save, score


def run(folder):
    import torch
    from peft import LoraConfig, PeftModel, TaskType, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed

    started = time.monotonic()
    cfg = json.loads((folder/'config.json').read_text())
    torch.set_num_threads(cfg['threads'])
    torch.use_deterministic_algorithms(True)
    set_seed(cfg['seed'])
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    frozen = json.loads((ROOT/'week08/data/freeze.json').read_text())
    rows = [json.loads(x) for x in (ROOT/'week08/data/validation.jsonl').read_text().splitlines()]
    tokenizer = AutoTokenizer.from_pretrained(cfg['model_id'], revision=cfg['revision'], cache_dir=str(ROOT/cfg['cache_dir']), local_files_only=True)
    tokenizer.pad_token = tokenizer.eos_token
    base = AutoModelForCausalLM.from_pretrained(cfg['model_id'], revision=cfg['revision'], cache_dir=str(ROOT/cfg['cache_dir']), local_files_only=True, dtype=torch.float32, attn_implementation='eager')
    base.eval()
    inputs = [tokenizer(frozen['prompt'].format(text=x['text']), return_tensors='pt', add_special_tokens=False) for x in rows]

    def logits(model):
        with torch.no_grad():
            return [model(**x, use_cache=False).logits.cpu() for x in inputs]

    def compare(left, right):
        diffs = [float((a-b).abs().max()) for a,b in zip(left,right)]
        return {'allclose': all(torch.allclose(a,b,atol=1e-4,rtol=1e-4) for a,b in zip(left,right)), 'max_abs_diff':max(diffs), 'per_prompt_max_abs_diff':diffs, 'atol':1e-4, 'rtol':1e-4, 'n_prompts':len(left)}

    base_logits = logits(base)
    fresh = get_peft_model(base, LoraConfig(task_type=TaskType.CAUSAL_LM, r=cfg['r'], lora_alpha=cfg['lora_alpha'], lora_dropout=0.0, target_modules=cfg['target_modules'], bias='none'))
    fresh.eval()
    named = dict(fresh.named_parameters())
    init = compare(base_logits, logits(fresh))
    init['all_B_zero'] = all(torch.count_nonzero(p).item()==0 for n,p in named.items() if 'lora_B' in n)
    init['all_A_nonzero'] = all(torch.count_nonzero(p).item()>0 for n,p in named.items() if 'lora_A' in n)
    init['A_initialization'] = 'PEFT default Kaiming uniform (paper uses Gaussian)'
    del named, base_logits
    base = fresh.unload()
    del fresh
    gc.collect()
    model = PeftModel.from_pretrained(base, folder/'adapter', is_trainable=False)
    model.eval()
    layers=[]
    for name, layer in model.named_modules():
        if hasattr(layer,'lora_A') and 'default' in layer.lora_A:
            a,b=layer.lora_A['default'].weight,layer.lora_B['default'].weight
            expected=(b@a)*(cfg['lora_alpha']/cfg['r'])
            actual=layer.get_delta_weight('default')
            layers.append({'name':name,'A_shape':list(a.shape),'B_shape':list(b.shape), 'rank_bound':cfg['r'], 'scaling':layer.scaling['default'], 'delta_nonzero':bool(torch.count_nonzero(actual).item()), 'formula_max_abs_diff':float((actual-expected).abs().max().detach()), 'formula_equal':bool(torch.equal(actual,expected))})
    unmerged=logits(model)
    merged=model.merge_and_unload(safe_merge=True)
    merged.eval()
    merge=compare(unmerged,logits(merged))
    merge['no_lora_parameters_remaining']=all('lora_' not in n for n,_ in merged.named_parameters())
    predictions=[]
    with torch.no_grad():
        for row,inp in zip(rows,inputs):
            seq=merged.generate(**inp,do_sample=False,max_new_tokens=cfg['max_new_tokens'],pad_token_id=tokenizer.pad_token_id,eos_token_id=tokenizer.eos_token_id,use_cache=True)
            predictions.append({'id':row['id'],'answer':row['answer'],'prediction':tokenizer.decode(seq[0,inp['input_ids'].shape[1]:],skip_special_tokens=True)})
    old=json.loads((folder/'after-predictions.json').read_text())
    merge['greedy_predictions_equal']=all(a['id']==b['id'] and a['prediction']==b['prediction'] for a,b in zip(old,predictions)) and len(old)==len(predictions)
    metrics=score(predictions)
    save(folder/'merged-predictions.json',predictions)
    save(folder/'merged-metrics.json',metrics)
    result={'initialization':init,'layers':layers,'merge':merge,'adapter_sha256':digest(folder/'adapter/adapter_model.safetensors'),'seconds':time.monotonic()-started}
    result['passed']=all([init['allclose'],init['all_B_zero'],init['all_A_nonzero'],len(layers)==60,all(x['formula_equal'] and x['delta_nonzero'] for x in layers),merge['allclose'],merge['greedy_predictions_equal'],merge['no_lora_parameters_remaining']])
    save(folder/'mechanism.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='layers'},ensure_ascii=False),flush=True)
    if not result['passed']:
        raise RuntimeError('Mechanism validation failed; see saved mechanism.json')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',required=True)
    args=parser.parse_args()
    run((ROOT/args.run).resolve())
