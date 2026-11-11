"""Recompute both tasks separately, retain all errors and generate a report."""
import argparse
import csv
import difflib
import random
from pathlib import Path
from common import ROOT, read, save, sha, verify, pdf_rows, score, aggregate, slices

REPORT = ROOT / 'week10/reports'


def interval(values, rng):
    samples = sorted(sum(rng.choices(values, k=len(values))) / len(values) for _ in range(2000))
    return [samples[49], samples[1949]]


def build(suite_file):
    protocol, docs = verify()
    state = read(suite_file)
    assert state['status'] == 'complete'
    assert state['protocol_sha256'] == sha(ROOT / 'week10/configs/protocol.json')
    results, errors, costs = {}, [], {}
    pdf_results = {}
    for label, run in [('pdf-baseline', protocol['pdf_baseline']), ('pdf-no-ocr', state['pdf_no_ocr'])]:
        rows, meta = pdf_rows(ROOT / run, docs)
        assert meta['status'] in ['completed', 'failed']
        assert all(r['status'] in ['completed', 'failed'] for r in meta['documents'])
        expected = read(ROOT / f'week10/configs/{label}.json')
        assert all(meta['config'][k] == v for k, v in expected.items() if k not in ['name', 'output_root'])
        results[label] = {'overall': aggregate(rows), 'slices': slices(rows, ['type','layout','scan_quality']), 'documents': rows}
        pdf_results[label] = rows
        costs[label] = {'seconds_including_per_page_load': sum(r['seconds'] for r in rows),
                        'gpu_hours': 0, 'paid_cost_cny': 0, 'peak_rss_mib': None,
                        'note': 'Baseline historical timing reused; no controlled speedup claim; PDF peak memory not measured.'}
        for r in rows:
            labels = []
            if not r['success']: labels.append('pipeline_output_failure')
            if not r['prediction']: labels.append('empty_output')
            if r['score'] < 1 - 1e-12: labels.append('content_sequence_mismatch')
            if r['reading_order'] is not None and r['reading_order'] < 1: labels.append('reading_order_or_missing_marker')
            if r['table_exact'] is False: labels.append('table_grid_or_span_mismatch')
            if labels:
                edits = []
                # Diagnostic excerpt only: does not change the Week07 scoring normalization.
                for op,i,j,k,l in difflib.SequenceMatcher(None,r['reference'],r['prediction'],autojunk=False).get_opcodes():
                    if op != 'equal': edits.append({'op':op,'reference':r['reference'][i:j],'prediction':r['prediction'][k:l]})
                errors.append({'case_id': f'{label}/{r["id"]}', 'task': 'pdf', 'method':label, 'id':r['id'],
                               'labels':labels, 'score':r['score'], 'raw':r['raw'], 'input':r['input'],
                               'reference_file':r['reference_file'], 'edits':edits,
                               'review_status':'pending_user', 'causal_claim':'candidate symptoms only; visual review required'})
    source_rows = [__import__('json').loads(x) for x in (ROOT / protocol['text_split']).read_text().splitlines()]
    for label, folder in state['text'].items():
        path = ROOT / folder
        rows, meta = read(path / 'predictions.json'), read(path / 'metadata.json')
        assert meta['status'] == 'complete'
        assert meta['predictions_sha256'] == sha(path / 'predictions.json')
        assert [(r['id'],r['text'],r['answer']) for r in rows] == [(r['id'],r['text'],r['answer']) for r in source_rows]
        for f, h in meta['source_sha256'].items(): assert sha(ROOT / f) == h
        metrics = score(rows)
        results[label] = {'overall': metrics | aggregate(rows), 'slices': slices(rows, ['template']), 'documents':rows}
        costs[label] = {k: meta[k] for k in ['load_seconds','total_seconds','peak_rss_mib','gpu_hours','paid_cost_cny']}
        costs[label]['inference_seconds'] = sum(r['seconds'] for r in rows)
        costs[label]['training_wandb_identity'] = meta.get('training_wandb_identity')
        for r in rows:
            if not r['exact']:
                labels = ['invalid_json'] if not r['json_valid'] else [k for k in ['total_correct','currency_correct'] if not r[k]] or ['extra_keys_or_schema']
                errors.append({'case_id':f'{label}/{r["id"]}', 'task':'text','method':label,'id':r['id'],
                               'labels':labels,'raw':f'{folder}/predictions.json','prediction':r['prediction'],
                               'reference':r['answer'],'review_status':'pending_user'})
    # Descriptive paired bootstrap; do not mix PDF and field-extraction metrics.
    rng = random.Random(protocol['bootstrap']['seed'])
    ci = {}
    for label, result in results.items():
        key = 'score' if label.startswith('pdf-') else 'exact'
        ci[label] = interval([float(r[key]) for r in result['documents']], rng)
    ci['pdf_no_ocr_minus_baseline'] = interval([b['score'] - a['score'] for a,b in zip(pdf_results['pdf-baseline'],pdf_results['pdf-no-ocr'])],rng)
    ci['text_a_minus_b'] = interval([float(a['exact']) - float(b['exact']) for a,b in zip(results['run-a']['documents'],results['run-b']['documents'])],rng)
    all_text = [[__import__('json').loads(x) for x in (ROOT / f'week08/data/{s}.jsonl').read_text().splitlines()] for s in ['train','validation','reserved-test']]
    leakage = {'exact_text_overlap': [len({r['text'] for r in all_text[i]} & {r['text'] for r in all_text[j]}) for i,j in [(0,1),(0,2),(1,2)]],
               'template_overlap':True, 'interpretation':'No exact-text duplicates; shared generator/templates prevent real-world generalization claims. Test now consumed; no later tuning on it.'}
    assert leakage['exact_text_overlap'] == [0,0,0]
    summary = {'suite':str(suite_file.relative_to(ROOT)), 'protocol_sha256':sha(ROOT/'week10/configs/protocol.json'),
               'results':results,'costs':costs,'bootstrap_95_percent':ci,'leakage':leakage,
               'error_case_count':len(errors),'error_unique_documents':len({(e['task'],e['id']) for e in errors}),
               'pdf_error_unique_documents':len({e['id'] for e in errors if e['task']=='pdf'}),
               'selection':'Keep OCR for PDF. Text adapters supported only on synthetic teaching task; no production adoption or A/B winner.'}
    REPORT.mkdir(exist_ok=True)
    save(REPORT / 'comparison.json', summary)
    save(REPORT / 'error-taxonomy.json', errors)
    review = REPORT / 'manual-review.csv'
    if not review.exists():
        with review.open('w',newline='') as f:
            fields = ['case_id','automatic_labels','human_labels','confirmed','notes']
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
            for e in errors: w.writerow({'case_id':e['case_id'],'automatic_labels':';'.join(e['labels'])})
    taxonomy = ['# 错误分类与原始证据', '', '以下为自动候选分类，尚未由本人目视确认。一个case是一个方法在一个文档上的失败；同一文档的跨方法错误会重复计数。内容差异可能来自顺序或OCR，不能仅凭编辑差异断定原因。', '',
                f'共 {len(errors)} 个错误case，涉及 {summary["error_unique_documents"]} 个任务内唯一文档；PDF部分涉及 {summary["pdf_error_unique_documents"]} 个唯一文档。保留全部失败，不为凑20例制造样本。', '',
                '| Case | 候选症状 | 原始证据 |', '| --- | --- | --- |']
    for e in errors:
        taxonomy.append(f'| {e["case_id"]} | {", ".join(e["labels"])} | [输出](../../{e["raw"]})' + (f' / [PDF](../../{e["input"]}) / [参考](../../{e["reference_file"]})' if e['task']=='pdf' else '') + ' |')
    (REPORT / 'error-taxonomy.md').write_text('\n'.join(taxonomy)+'\n')
    lines = ['# Week10 统一评测与消融实测报告', '',
             '本周采用两个任务各自统一的协议。Week07中文PDF参考是正文/顺序/表格，Week09 adapter输出英文账单JSON，不能使用同一个指标比较。课程“在Week07 test上评测Week09 runs”这一字面要求未满足；替代实验明确分开，保留该限制。没有把reference文本当模型输入。', '',
             '## PDF：冻结24页、原指标、关闭OCR消融', '',
             '| 方法 | n | 内容相似度 | 阅读顺序 | 表格严格匹配 | 总秒数 |', '| --- | --- | --- | --- | --- | --- |']
    for label in pdf_results:
        m = results[label]['overall']
        lines.append(f'| {label} | {m["n"]} | {m["score"]:.6f} | {m["reading_order"]:.6f} | {m["table_exact"]:.2%} | {m["total_seconds"]:.1f} |')
    lines += ['', 'baseline复用Week07原始输出并重新认证哈希、重新评分；no-OCR为本周新运行。所有24页包括失败均计分。关闭OCR时扫描页可能转换退出0但因空输出未通过既有机械检查，pipeline记failed、按原协议计0；这类预期负面结果不重试改写。算法配置唯一差异do_ocr；name/output_root是实验标签/存放位置。历史与本轮耗时含每页新进程和模型加载，不能据此宣称严格加速比。PDF峰值内存历史未测量，保持缺失。', '',
              '## 文本抽取：首次消费12条reserved-test', '',
              '| 方法 | n | JSON exact | JSON有效率 | 推理秒数 | 加载及评测总秒数 | 峰值MiB |', '| --- | --- | --- | --- | --- | --- | --- |']
    for label in state['text']:
        m,c = results[label]['overall'],costs[label]
        lines.append(f'| {label} | {m["n"]} | {m["exact_rate"]:.2%} | {m["json_valid_rate"]:.2%} | {c["inference_seconds"]:.2f} | {c["total_seconds"]:.2f} | {c["peak_rss_mib"]:.1f} |')
    lines += ['', 'base、A、B均在CPU/float32/2线程、seed42、同Prompt、greedy最多32新token条件下执行，各自独立进程加载；不训练、不修改checkpoint。A/B训练历史只差学习率0.001/0.0005；base对A是关闭/启用已训练adapter的消融，不是新训练消融。这里只测任务exact，未计算测试NLL。', '',
              '## 切片与成本探索', '', '| 方法 | 分组 | n | 主指标 |', '| --- | --- | --- | --- |']
    for label,r in results.items():
        for key, groups in r['slices'].items():
            for group,m in groups.items():
                value = m['score'] if label.startswith('pdf-') else m['exact']
                lines.append(f'| {label} | {key}={group} | {m["n"]} | {value:.6f} |')
    lines += ['', '自主探索选择“成本”：比较两项任务的实际推理/加载耗时、可用内存记录和维护边界。CPU本机运行，新增付费云费用0，GPU小时0；电费、虚拟机购置费用和能耗未测，不能称总成本为0。成本采样无重复，其他进程竞争可能影响结果。LoRA训练历史成本见Week09，不能把本轮评测时间当训练成本。', '',
              '## 置信区间、错误和选择', '',
              '固定seed42，按文档进行2000次bootstrap；差异使用相同重采样索引的配对差。描述性95%区间如下；样本极小且模板共享，全对时bootstrap退化为[1,1]，不能解释成总体成功概率必为100%。单seed不支持训练随机性结论。', '', '```json', __import__('json').dumps(ci,indent=2), '```', '',
              f'错误候选共{len(errors)}例，详见[全部错误及输入链接](error-taxonomy.md)和[结构化差异](error-taxonomy.json)。人工复核待本人填写[CSV](manual-review.csv)。重复文档与不同方法的case数分别统计。', '',
              '事实：上表数字由冻结输入和原始输出重算。解释：关闭OCR后的变化检验扫描文档对OCR依赖；文本adapter效果只涉及同模板英文数据。推测：真实中文PDF、版面与噪声条件下仍有效，当前没有证据。', '',
              '决定：PDF继续保留OCR；不采用无OCR作为全类型默认。英文文本adapter仅保留作教学候选，不部署生产；不凭单次耗时或验证NLL宣布A/B胜者。若要进一步调参，使用dev/validation，另备新最终测试；本轮test已被诊断查看，不再充当未见数据。', '',
              '限制：固定合成数据、共同模板、参考来自生成规格且人工核验待完成；PDF基线复用历史输出；没有公共benchmark排名、无多seed训练、无受控计时复测、无W&B云端Report。', '',
              'W&B：本轮评测为本地JSON，不声称创建了云端评测run。训练project为multimodal-ai-bootcamp-week09，A离线ID=3xryklnu，B=0h6gfu6a，artifact本地digest与文件SHA见对应Week09 artifact-manifest。entity、artifact :vN、云端Report URL仍待本人登录同步。', '',
              f'复现入口及参数见[README](../README.md)。本报告输入suite：`{suite_file.relative_to(ROOT)}`；协议SHA256：`{summary["protocol_sha256"]}`。AI完成代码、执行和自动核验，本人尚未人工确认。']
    (REPORT / 'evaluation-report.md').write_text('\n'.join(lines)+'\n')
    # Export a standalone static figure for VS Code / GitHub viewing.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1,2,figsize=(10,4))
    for ax,names,key,title in [(axes[0],list(pdf_results),'score','PDF content similarity (n=24)'),(axes[1],list(state['text']),'exact','Text JSON exact (n=12)')]:
        vals = [results[n]['overall'][key] for n in names]
        ax.bar(names,vals,color=['#607d8b','#26a69a','#ffb74d'][:len(names)])
        ax.set_ylim(0,1.1); ax.set_title(title)
        for i,v in enumerate(vals):ax.text(i,v+.025,f'{v:.3f}',ha='center')
    fig.tight_layout(); fig.savefig(REPORT/'comparison.png',dpi=160); plt.close(fig)
    receipt_paths = set(protocol['files'])
    receipt_paths.update(str(f.relative_to(ROOT)) for f in (ROOT/'week10/scripts').glob('*.py'))
    receipt_paths.add('week10/run.py')
    receipt_paths.add(str(suite_file.relative_to(ROOT)))
    for folder in state['text'].values():
        receipt_paths.update(str(f.relative_to(ROOT)) for f in (ROOT/folder).glob('*.json'))
    for folder in [protocol['pdf_baseline'],state['pdf_no_ocr']]:
        run = ROOT/folder
        receipt_paths.add(f'{folder}/run-metadata.json')
        for rec in read(run/'run-metadata.json')['documents']:
            receipt_paths.update(str((run / f['file']).relative_to(ROOT)) for f in rec['output_files'])
    receipt_paths.update(f'week10/reports/{n}' for n in ['comparison.json','error-taxonomy.json','evaluation-report.md','error-taxonomy.md','comparison.png'])
    save(ROOT / 'week10/evidence/manifest.json', {'suite':str(suite_file.relative_to(ROOT)), 'files':{f:sha(ROOT/f) for f in sorted(receipt_paths)},'manual_review':'Excluded from receipt to allow human completion; currently pending'})
    print({'error_cases':len(errors),'unique_documents':summary['error_unique_documents'],'results':{k:v['overall'] for k,v in results.items()}},flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--suite', type=Path, required=True, help='Explicit completed suite.json; no implicit best/latest selection')
    build(ap.parse_args().suite.resolve())
