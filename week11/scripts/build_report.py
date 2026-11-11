"""Build a local report from one explicitly selected Week11 suite."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from week08.train import digest, save


def fenced(value, language='text'):
    # Generated text can itself contain Markdown fences; keep it literal.
    ticks='`'*max(3, max((len(x) for x in re.findall(r'`+',value)),default=0)+1)
    return f'{ticks}{language}\n{value}\n{ticks}'


def refresh_manifest():
    excluded={'week11/evidence/manifest.json','week11/evidence/verification.json','week11/reports/manual-review.md'}
    files={str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'week11').rglob('*')) if p.is_file() and '__pycache__' not in p.parts and str(p.relative_to(ROOT)) not in excluded}
    save(ROOT/'week11/evidence/manifest.json',{'algorithm':'sha256','files':files,'mutable_human_review':'week11/reports/manual-review.md','excluded_generated':['week11/evidence/manifest.json','week11/evidence/verification.json']})


def build(path):
    suite=json.loads(path.read_text())
    if suite['status']!='complete': raise ValueError('Cannot report incomplete suite as complete')
    results={}
    for rank,folder in suite['runs'].items():
        p=ROOT/folder
        meta=json.loads((p/'metadata.json').read_text())
        comp=json.loads((p/'comparison.json').read_text())
        mech=json.loads((p/'mechanism.json').read_text())
        results[rank]={'folder':folder,'baseline':comp['baseline'],'after':comp['after'],'trainable_parameters':meta['trainable_parameters'],'total_parameters':meta['total_parameters'],'trainable_fraction':meta['trainable_parameters']/meta['total_parameters'],'training_seconds':meta['training_seconds'],'total_seconds':meta['total_seconds'],'peak_rss_mib':meta['peak_rss_mib'],'adapter_bytes':(p/'adapter/adapter_model.safetensors').stat().st_size,'frozen_base_equal':meta['frozen_base_before_sha256']==meta['frozen_base_after_sha256'],'reload_equal':meta['reload_predictions_equal'],'mechanism_passed':mech['passed'],'merge_max_abs_diff':mech['merge']['max_abs_diff'],'merge_greedy_equal':mech['merge']['greedy_predictions_equal'],'init_max_abs_diff':mech['initialization']['max_abs_diff']}
    r4,r8=results['4'],results['8']
    criteria={'r4_exact_at_least_075':r4['after']['exact_rate']>=.75,'r4_improvement_at_least_050':r4['after']['exact_rate']-r4['baseline']['exact_rate']>=.5,'both_under_one_percent':all(x['trainable_fraction']<.01 for x in results.values()),'both_base_frozen':all(x['frozen_base_equal'] for x in results.values()),'both_reload_equal':all(x['reload_equal'] for x in results.values()),'parameter_ratio_1_to_2':r8['trainable_parameters']==2*r4['trainable_parameters'],'both_mechanism_passed':all(x['mechanism_passed'] for x in results.values())}
    summary={'suite':str(path.relative_to(ROOT)),'preregistered_commit':suite['preregistered_commit'],'results':results,'criteria':criteria,'all_local_criteria_passed':all(criteria.values()),'human_review_complete':False}
    save(ROOT/'week11/reports/comparison.json',summary)
    table=[]
    for rank,x in results.items():
        table.append(f"| r{rank} | {x['baseline']['exact_rate']:.1%} → {x['after']['exact_rate']:.1%} | {x['after']['json_valid_rate']:.1%} | {x['baseline']['answer_nll']:.6f} → {x['after']['answer_nll']:.6f} | {x['trainable_parameters']:,} ({x['trainable_fraction']:.3%}) | {x['training_seconds']:.2f} / {x['total_seconds']:.2f} | {x['peak_rss_mib']:.1f} |")
    case_lines=[]
    candidates=[]
    for rank,folder in suite['runs'].items():
        p=ROOT/folder
        before=json.loads((p/'baseline-predictions.json').read_text())
        after=json.loads((p/'after-predictions.json').read_text())
        for a,b in zip(before,after):
            if not a['exact'] or not b['exact']:
                candidates.append({'rank':rank,'id':a['id'],'baseline':a['prediction'],'after':b['prediction'],'reference':a['answer'],'baseline_exact':a['exact'],'after_exact':b['exact'],'human_review':'pending'})
        for a,b in list(zip(before,after))[:2]:
            case_lines.extend([f"### rank{rank} / {a['id']}","",'输入Prompt：',fenced(a['prompt']),'参考：`'+json.dumps(a['answer'],ensure_ascii=False)+'`',"",'训练前：',fenced(a['prediction']),'训练后：',fenced(b['prediction'],'json'),""])
    save(ROOT/'week11/reports/error-candidates.json',candidates)
    (ROOT/'week11/reports/cases.md').write_text('# 原始预测摘录（自动选取，每run前两条）\n\n完整错误候选见[JSON](error-candidates.json)，人工复核未完成。\n\n'+'\n'.join(case_lines))
    rank_interpretation=('两run在这12条上同分，无法区分生成准确率；这不是等效性证明。' if r4['after']['exact_rate']==r8['after']['exact_rate'] else '两run在这12条上有差异，但单seed不足以判断普遍优劣。')
    state='全部达到' if all(criteria.values()) else '部分未达到，按预定标准保留负面结果'
    text=f'''# Week11 reproduction report

## 结论与证据范围

本地预定标准：**{state}**。这是LoRA机制与小型下游任务的迁移验证。训练结果、基座冻结和合并检查分别判断；不等同于复现原论文的完整结论或benchmark。

计划提交：`{suite['preregistered_commit']}`。运行入口记录：[suite](../{path.relative_to(ROOT/'week11')})；先有计划/配置提交，再有本次原始训练。制定计划时已知旧r8在同一validation表现良好，因此存在历史结果选择偏差。本人阅读与复核状态：待完成。

## 实测结果

相同96 train / 12 validation，seed42，60步，固定最终checkpoint。JSON exact是字典严格比较，字段是字符串，不允许额外字段或围栏。数据来自虚构账单，非PDF/图像输入。

| Run | strict exact（前→后） | 训练后JSON合法率 | 答案NLL（前→后） | 可训练参数 / 总参数占比 | 训练/训练脚本总秒数 | 峰值RSS MiB |
| --- | --- | --- | --- | --- | --- | --- |
{chr(10).join(table)}

RSS由每个训练子进程记录，含模型/框架/optimizer；不是GPU显存，也没有全参数训练内存对照。脚本总时间不含另起进程的机制核验，机制时间见各mechanism.json。GPU小时0、付费云费用0。

| 检查 | r4 | r8 |
| --- | --- | --- |
| 非LoRA权重前后SHA256一致 | {r4['frozen_base_equal']} | {r8['frozen_base_equal']} |
| adapter重加载预测一致 | {r4['reload_equal']} | {r8['reload_equal']} |
| 初始化logits最大绝对差 | {r4['init_max_abs_diff']:.8g} | {r8['init_max_abs_diff']:.8g} |
| 合并logits最大绝对差（12条、全部Prompt token位置） | {r4['merge_max_abs_diff']:.8g} | {r8['merge_max_abs_diff']:.8g} |
| 合并greedy文本逐条一致 | {r4['merge_greedy_equal']} | {r8['merge_greedy_equal']} |
| adapter文件字节数 | {r4['adapter_bytes']} | {r8['adapter_bytes']} |

完整标准布尔值见[comparison.json](comparison.json)。全部60个q/v层的矩阵形状、缩放与delta核验见各run的mechanism.json。合并只在内存执行，不上传整份模型。

## 原文设置与本地差异

| 项目 | 论文 | 本地 | 对解释的影响 |
| --- | --- | --- | --- |
| 模型 | GPT-2/3、RoBERTa、DeBERTa等，见§5 | SmolLM2-135M | 不能比较原表分数或外推规模效应 |
| 数据/任务 | 多个公开NLP任务，见§5与附录 | 96/12同模板合成账单 | 仅开发集现象，不能证明真实文档泛化 |
| 实现 | 作者microsoft/LoRA（loralib） | 复用Week08，PEFT0.19.0 | 独立实现机制核验，非原作者脚本原样运行 |
| 初始化 | §4.1：A Gaussian、B零 | PEFT默认A Kaiming uniform、B零 | 保留零初始增量，A分布不同 |
| rank探索 | §7.2/Table6在论文任务中比较多个rank | r4/r8，alpha恒16 | alpha/r亦改变，不能解释为纯容量效应 |
| 对照 | 包含full fine-tuning等 | 只有同base训练前baseline与两rank | 不检验LoRA追平/超越全参微调 |
| 训练/重复 | 依任务调超参，部分报告多seed | 单seed、固定60步 | 不报告稳定性或统计优越性 |
| 部署 | §4.1说明合并可去掉支路 | 核对合并后的logits与生成 | 不测零延迟或速度提升 |

论文依据：[原文v2 §4.1/§5/§7.2](https://arxiv.org/html/2106.09685v2)、[作者代码](https://github.com/microsoft/LoRA)。这里的本地结论来自本仓库原始结果。

## 失败、负面证据与解释

- [原始案例](cases.md)保留训练前的格式失败；[错误候选](error-candidates.json)包含所有baseline或训练后不匹配的run×样本，人工栏待本人。没有为凑数生成失败预测。
- r4训练后strict exact={r4['after']['exact_rate']:.1%}，r8={r8['after']['exact_rate']:.1%}。{rank_interpretation}
- 参数量减半不等于总体内存减半：本次r4峰值RSS={r4['peak_rss_mib']:.1f}MiB，r8={r8['peak_rss_mib']:.1f}MiB；单次进程记录不能证明更低rank稳定节省总内存，也没有分析差异原因。
- 事实：参数量呈1:2；本地是否改善与合并核验由上表直接支持。解释：结果与低秩支路能承担该局部适配相符。推测：模板记忆和格式学习可能贡献很大，需要新开发数据验证。
- 已知负面条件：币种与模板完全相关；validation过去已多次使用；更低NLL不代表greedy正确。未进行新独立最终测试，不把Week10的旧test改名复用。
- 机制检查通过也不足以证明权重更新的“最优内在秩”。BA的秩上界来自参数形状，未从中声称测得任务真实内在维度。

## 项目决定与下一步

可保留LoRA作为CPU教学及文档文字抽取后的适配方案；当前证据不足以决定生产采用或宣称最优rank。下一步在新开发集打破模板/币种相关性，保留新最终测试；先定义接口，再考虑接入Docling。此建议未在本周执行。

## 可复现与人工核验

输入SHA、源码/计划快照、模型revision、配置、训练日志和小adapter见suite；[唯一入口](../README.md)含所有命令作用。[AI披露](../evidence/ai-usage.md)区分机器核验与本人核验。当前VM已真实运行，未声称全新机器复现或ACM徽章认证。最后由本人按[收尾清单](manual-review.md)抽查原文、样例、理解并填写学习时间。
'''
    (ROOT/'week11/reports/reproduction-report.md').write_text(text)
    refresh_manifest()
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite',required=True)
    args=parser.parse_args()
    build(ROOT/args.suite)
