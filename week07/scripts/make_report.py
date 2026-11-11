"""从一次完整评测生成只读报告与集中核验清单；不更新冻结数据。"""
import argparse
import difflib
import json
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
WEEK=ROOT/'week07'
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--run',type=Path,required=True); args=p.parse_args()
    
    if (WEEK/'reports/benchmark-report.md').exists() or (WEEK/'reports/manual-review.md').exists():
        p.exit(2, '报告或本人核验清单已存在，拒绝覆盖；请保留首次报告并为新运行另建报告。\n')
    run=args.run.resolve(); result=json.loads((run/'evaluation.json').read_text()); overall=result['overall']
    relative=str(run.relative_to(WEEK)); docs={x['id']:x for x in result['documents']}
    def fmt(value): return '—' if value is None else f'{value:.4f}'
    text=['# Week07 Benchmark Report','',
          '状态：Codex已实际执行24页baseline和自动评测；本人视觉核验、实际学习时间和自评待补。结果仅适用于本地自制教学测试集v1。','',
          '## 协议与baseline','',
          '先生成参考、冻结24个test/3个dev输入及指标/配置，再运行Week06原有Docling CPU Pipeline。OCR和accurate表格模式保持不变，无Prompt、训练或test调参；dev尚未使用。基准模型与锁定依赖见第6周证据。', '',
          f'原始运行：[{run.name}](../{relative}/)；[指标原始JSON](../{relative}/evaluation.json)；[输入与配置冻结](../data/freeze.json)。运行元数据中的Git提交为本周提交前的基底，实际源码有快照/哈希，最终归档见Git历史。','',
          '主指标是逐页规范化字符编辑相似度宏平均，0–1、越高越好；失败页计0并留在分母。辅助项按适用页计算。详细定义先于推理保存在 [evaluation.json](../configs/evaluation.json)，不是官方OmniDocBench评分，也不是生产准确率。','',
          '## 总体与切片','',
          '| 分组 | 页数 | 字符相似度 | 转换成功率 | 标记对顺序 | 表格精确匹配 | 总秒数 |','| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for label,x in [('总体',overall)]+[(f'{key}={v}',s) for key,values in result['slices'].items() for v,s in values.items()]:
        text.append(f"| {label} | {x['n']} | {fmt(x['score'])} | {fmt(x['success_rate'])} | {fmt(x['reading_order'])} | {fmt(x['table_exact'])} | {x['total_seconds']:.2f} |")
    text+=['','耗时为各页墙钟时间相加，包含各自子进程/模型加载与OCR；不等于纯模型速度、总学习时间或跨机器性能比较。扫描4档每档2页，DPI/旋转/模糊共同变化，仅为描述性切片。','',
           '## 最差五例（先定规则，后排序）','',
           '按主指标升序、ID升序取5页，包含相同模板的重复错误，不替换成更丰富的故事。以下差异是Codex对生成参考和原始预测的自动定位，具体视觉判断待本人核验。','']
    selected=result['worst_five']
    best=max(result['documents'],key=lambda x:(x['score'],x['id']))['id']
    manual=['# 本人最后集中完成的核验','',
            '实验已由Codex代运行；不用重复安装或重跑模型。下列参考由生成规格给出，需你亲自对照PDF；可在VS Code中打开PNG预览及对应Markdown/JSON。不要编辑原始预测或冻结v1参考。','',
            '请逐项在“本人反馈”写一句具体观察；若找到参考错误，先记录，另建数据版本统一重评。','',
            '| 样例 | 自动字符分 | PDF / 预览 / 原始输出 | 本人反馈 |','| --- | ---: | --- | --- |']
    for ident in selected+[best]:
        doc=docs[ident]; preview=WEEK/f'reports/previews/{ident}.png'
        subprocess.run(['pdftoppm','-scale-to','1200','-singlefile','-png',str(WEEK/f'data/test/{ident}.pdf'),str(preview.with_suffix(''))],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        manual.append(f"| {ident} {'（最好一例）' if ident==best else ''} | {doc['score']:.4f} | [PDF](../data/test/{ident}.pdf) · [预览](previews/{ident}.png) · [MD](../{relative}/{ident}/document.md) · [JSON](../{relative}/{ident}/document.json) | 待本人填写 |")
        if ident not in selected: continue
        a=''.join(doc['reference_blocks']); b=''.join(doc['prediction_blocks'])
        import sys
        sys.path.insert(0,str(WEEK/'scripts'))
        from evaluate import norm
        a,b=norm(a),norm(b)
        changes=[]
        for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
            if tag!='equal': changes.append({'operation':tag,'expected':a[i:j],'predicted':b[k:l]})
        text += [f"### {ident}｜{doc['type']}｜{doc['score']:.4f}",'',
                 f'[原页预览](previews/{ident}.png) · [原始Markdown](../{relative}/{ident}/document.md) · [原始JSON](../{relative}/{ident}/document.json) · [生成参考](../references/{ident}.json)','',
                 f"标记对顺序={fmt(doc['reading_order'])}；表格精确匹配={doc['table_exact']}；转换成功={doc['success']}。",'',
                 '规范化差异定位（这是字符串对齐线索，不保证每段都能独立归因为OCR）：','',
                 '```json',json.dumps(changes,ensure_ascii=False,indent=2),'```','']
    text += ['## 数据泄漏与负责任使用','',
             'test与dev、旧三页PDF无精确哈希重复；新test不训练、不调参，原始输出未手改。生成参考先于预测，排除按模型答案补标成功的做法。','',
             '**不能排除的偏差**：dev/test共享绘制模板，24页内容简单且相关；模型可能见过类似格式。只有哈希检查不能证明统计独立、没有预训练污染或现实代表性。新文档降低原页重复风险，但无法证明完全无污染。','',
             '新内容为CC0虚构教学材料，不含真实隐私；字体和模型许可分别继承已核对的第5/6周来源，见 [Dataset Card](../dataset-card.md)。没有私人文档上传或付费API调用。','',
             '## 限制与下一步','',
             '自动指标不评价所有结构：标点、空格、标题层级、公式、证据定位和真实长文档未覆盖。表格结构另测，不能把字符分高视为完全解析正确。原始模型失败和参考定义错误也需要分开。','',
             '自主探索选择“数据分布与切片”，结果见上表；没有用test改模型，也没有把扫描档位视为单变量因果实验。本人按 [集中核验清单](manual-review.md) 对照最差五页和一页最好结果，再说明一处自动分数遗漏的问题。','',
             '下周先另建训练/验证数据；本轮test保持冻结。如果参考需修正，保留v1并建立新版本，对全部方法统一重评。真实泛化需另建跨模板/真实授权文档测试集。']
    manual+=['','重点：确认原页的关键内容是否与生成参考一致；检查预测是漏字/错字、顺序改变、表格关系错误，还是仅标点/版式差异。','',
             '完成六页后集中反馈：','',
             '1. 选一页说明“原页是什么、预测是什么、分数说明什么”。','2. 指出一处字符指标没反映的现象，例如标点、标题角色或表格关系；不要只凭分数猜测。',
             '3. 用一句话说明test/dev区别，以及下周为什么不能拿test训练。','4. 填写本人实际学习小时数、自主阶段和例会演练情况。','',
             '自评可选：未形成 / 已跑通 / 可复现 / 可解释 / 可扩展。当前自动运行不能代替本人学习自评。','',
             'GitHub同步由Codex完成后见分支；本人无需提供密钥。当前表格和复盘保持待填写，不代写为已经观察。']
    (WEEK/'reports/benchmark-report.md').write_text('\n'.join(text)+'\n')
    (WEEK/'reports/manual-review.md').write_text('\n'.join(manual)+'\n')
    print('已生成 benchmark-report.md、manual-review.md 和6页预览。')
if __name__=='__main__': main()
