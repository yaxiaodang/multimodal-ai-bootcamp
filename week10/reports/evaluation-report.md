# Week10 统一评测与消融实测报告

本周采用两个任务各自统一的协议。Week07中文PDF参考是正文/顺序/表格，Week09 adapter输出英文账单JSON，不能使用同一个指标比较。课程“在Week07 test上评测Week09 runs”这一字面要求未满足；替代实验明确分开，保留该限制。没有把reference文本当模型输入。

## PDF：冻结24页、原指标、关闭OCR消融

| 方法 | n | 内容相似度 | 阅读顺序 | 表格严格匹配 | 总秒数 |
| --- | --- | --- | --- | --- | --- |
| pdf-baseline | 24 | 0.967559 | 0.708333 | 0.00% | 996.4 |
| pdf-no-ocr | 24 | 0.650709 | 0.500000 | 0.00% | 352.1 |

baseline复用Week07原始输出并重新认证哈希、重新评分；no-OCR为本周新运行。所有24页包括失败均计分。关闭OCR时扫描页可能转换退出0但因空输出未通过既有机械检查，pipeline记failed、按原协议计0；这类预期负面结果不重试改写。算法配置唯一差异do_ocr；name/output_root是实验标签/存放位置。历史与本轮耗时含每页新进程和模型加载，不能据此宣称严格加速比。PDF峰值内存历史未测量，保持缺失。

## 文本抽取：首次消费12条reserved-test

| 方法 | n | JSON exact | JSON有效率 | 推理秒数 | 加载及评测总秒数 | 峰值MiB |
| --- | --- | --- | --- | --- | --- | --- |
| base | 12 | 0.00% | 0.00% | 32.82 | 39.04 | 1152.3 |
| run-a | 12 | 100.00% | 100.00% | 18.42 | 24.41 | 1152.3 |
| run-b | 12 | 100.00% | 100.00% | 15.78 | 23.51 | 1152.1 |

base、A、B均在CPU/float32/2线程、seed42、同Prompt、greedy最多32新token条件下执行，各自独立进程加载；不训练、不修改checkpoint。A/B训练历史只差学习率0.001/0.0005；base对A是关闭/启用已训练adapter的消融，不是新训练消融。这里只测任务exact，未计算测试NLL。

## 切片与成本探索

| 方法 | 分组 | n | 主指标 |
| --- | --- | --- | --- |
| pdf-baseline | type=digital | 8 | 1.000000 |
| pdf-baseline | type=scan | 8 | 0.950549 |
| pdf-baseline | type=table | 8 | 0.952128 |
| pdf-baseline | layout=single_column | 12 | 0.967033 |
| pdf-baseline | layout=table | 8 | 0.952128 |
| pdf-baseline | layout=two_column | 4 | 1.000000 |
| pdf-baseline | scan_quality=0 | 2 | 0.956044 |
| pdf-baseline | scan_quality=1 | 2 | 0.945055 |
| pdf-baseline | scan_quality=2 | 2 | 0.901099 |
| pdf-baseline | scan_quality=3 | 2 | 1.000000 |
| pdf-no-ocr | type=digital | 8 | 1.000000 |
| pdf-no-ocr | type=scan | 8 | 0.000000 |
| pdf-no-ocr | type=table | 8 | 0.952128 |
| pdf-no-ocr | layout=single_column | 12 | 0.333333 |
| pdf-no-ocr | layout=table | 8 | 0.952128 |
| pdf-no-ocr | layout=two_column | 4 | 1.000000 |
| pdf-no-ocr | scan_quality=0 | 2 | 0.000000 |
| pdf-no-ocr | scan_quality=1 | 2 | 0.000000 |
| pdf-no-ocr | scan_quality=2 | 2 | 0.000000 |
| pdf-no-ocr | scan_quality=3 | 2 | 0.000000 |
| base | template=0 | 4 | 0.000000 |
| base | template=1 | 4 | 0.000000 |
| base | template=2 | 4 | 0.000000 |
| run-a | template=0 | 4 | 1.000000 |
| run-a | template=1 | 4 | 1.000000 |
| run-a | template=2 | 4 | 1.000000 |
| run-b | template=0 | 4 | 1.000000 |
| run-b | template=1 | 4 | 1.000000 |
| run-b | template=2 | 4 | 1.000000 |

自主探索选择“成本”：比较两项任务的实际推理/加载耗时、可用内存记录和维护边界。CPU本机运行，新增付费云费用0，GPU小时0；电费、虚拟机购置费用和能耗未测，不能称总成本为0。成本采样无重复，其他进程竞争可能影响结果。LoRA训练历史成本见Week09，不能把本轮评测时间当训练成本。

## 置信区间、错误和选择

固定seed42，按文档进行2000次bootstrap；差异使用相同重采样索引的配对差。描述性95%区间如下；样本极小且模板共享，全对时bootstrap退化为[1,1]，不能解释成总体成功概率必为100%。单seed不支持训练随机性结论。

```json
{
  "pdf-baseline": [
    0.9535402540721692,
    0.9803795495284859
  ],
  "pdf-no-ocr": [
    0.449468085106383,
    0.8191489361702128
  ],
  "base": [
    0.0,
    0.0
  ],
  "run-a": [
    1.0,
    1.0
  ],
  "run-b": [
    1.0,
    1.0
  ],
  "pdf_no_ocr_minus_baseline": [
    -0.5123626373626374,
    -0.1543040293040293
  ],
  "text_a_minus_b": [
    0.0,
    0.0
  ]
}
```

错误候选共42例，详见[全部错误及输入链接](error-taxonomy.md)和[结构化差异](error-taxonomy.json)。人工复核待本人填写[CSV](manual-review.csv)。重复文档与不同方法的case数分别统计。

事实：上表数字由冻结输入和原始输出重算。解释：关闭OCR后的变化检验扫描文档对OCR依赖；文本adapter效果只涉及同模板英文数据。推测：真实中文PDF、版面与噪声条件下仍有效，当前没有证据。

决定：PDF继续保留OCR；不采用无OCR作为全类型默认。英文文本adapter仅保留作教学候选，不部署生产；不凭单次耗时或验证NLL宣布A/B胜者。若要进一步调参，使用dev/validation，另备新最终测试；本轮test已被诊断查看，不再充当未见数据。

限制：固定合成数据、共同模板、参考来自生成规格且人工核验待完成；PDF基线复用历史输出；没有公共benchmark排名、无多seed训练、无受控计时复测、无W&B云端Report。

W&B：本轮评测为本地JSON，不声称创建了云端评测run。训练project为multimodal-ai-bootcamp-week09，A离线ID=3xryklnu，B=0h6gfu6a，artifact本地digest与文件SHA见对应Week09 artifact-manifest。entity、artifact :vN、云端Report URL仍待本人登录同步。

复现入口及参数见[README](../README.md)。本报告输入suite：`week10/runs/suite-20261111T080142898866Z/suite.json`；协议SHA256：`23fe0eee490d2e771c3a02413a025dc8d8726ed74e0f971f7f74a66f056ab618`。AI完成代码、执行和自动核验，本人尚未人工确认。
