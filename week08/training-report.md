# Week08 真实训练报告

日期：2026-11-11（Asia/Shanghai）。AI代执行，本人阅读与视觉/字段核验待完成。所有数值来自下列本地运行，不是预期值或模拟数据。

## 问题与结论

135M英语base model在冻结的12条合成账单validation上，训练前严格字段完全正确为0/12。两次60步LoRA后结果见下表。此证据支持小型同模板任务上的JSON格式遵循与字段复制改善，不支持真实票据、PDF解析、视觉理解或跨领域能力提升。没有改进Week07 Docling baseline，也未运行其test来选择参数。

## 同协议前后对比

| 方法 | 学习率 | 字段完全正确 | JSON可解析 | total准确 | currency准确 | 答案token平均NLL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Base（两次相同） | — | 0.00% | 0.00% | 0.00% | 0.00% | 1.24116823 |
| A | 0.001 | 100.00% | 100.00% | 100.00% | 100.00% | 0.00024795 |
| B | 0.0005 | 100.00% | 100.00% | 100.00% | 100.00% | 0.00074655 |

每格都基于同一12条validation。解码为greedy、最多32个新token，不补JSON、不抽取片段后修复；JSON键顺序和空格不影响匹配，但字符串类型、字段值及额外字段会影响。NLL按参考答案及EOS的token数加权。Base不是instruct模型，0分不代表完全看不懂金额，不能推广为模型总体能力为零。

A/B只有learning_rate不同，name仅输出标签；两次baseline原始预测逐字节相同，source与base权重哈希相同。单seed、极小同模板数据不足以判断学习率优劣；如果生成率相同，NLL差异也不能解释成任务准确率提升。最终固定60步，没有挑最好checkpoint。探索不新增参数搜索。

## 训练配置、资源和产物

- 模型：`HuggingFaceTB/SmolLM2-135M`，revision `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`，Apache-2.0；模型卡副本见[evidence](evidence/base-model-card.md)。
- 环境：Python 3.10、torch 2.14.0+cpu、transformers 5.17.0、peft 0.19.0、accelerate 1.12.0；CPU FP32、2线程、seed=42。
- LoRA：r=8、alpha=16、dropout=0、q_proj/v_proj、bias=none；AdamW、weight_decay=0、梯度裁剪1.0；batch2×accumulation2，有效batch4；60步约2.5 epochs，最长样例82 tokens，上限192。
- 可训练参数：460,800 / 含adapter总参数 134,975,808，占0.341%；仅lora_参数可训练，base训练前后SHA-256相同。
- 运行代码Git基底：`8c5972295bdd675061dadd7deeca53bfd0a606af`；工作区含旧周未提交修改，未用于本周训练；代码、冻结清单及计划快照与SHA-256在每个run中。

| run | 实际训练时间 | 全流程时间 | 进程峰值RSS | adapter大小 | 成本 |
| --- | ---: | ---: | ---: | ---: | --- |
| A | 203.90s | 307.68s | 1539.05 MiB | 1.77 MiB | GPU 0h / 0元 |
| B | 209.92s | 291.04s | 1490.39 MiB | 1.77 MiB | GPU 0h / 0元 |

RSS是单进程高水位，包括模型、评价和哈希临时内存；不是训练张量显存。全流程包括模型加载、生成、哈希和重加载。A有网络探测重试，B离线，故总时间差不能视为学习率影响。两次均低于训练15分钟预算；没有付费服务、OOM或失败训练。准备阶段的Python ABI错误、沙箱网络重试和PEFT配置查找警告见[准备记录](evidence/setup-notes.md)与原始console，未删除或伪装成训练结果。

每个adapter约1.8MiB，已保存safetensors、adapter_config及模型卡；加载仍依赖相同base/tokenizer。两次均从磁盘重加载并在全部12条上重生成，与保存前预测完全一致。基础模型权重不提交；模型revision与下载入口可定位。

## 三个具体失败与变化案例

以下保留原始baseline字符串，不手工修复；训练后输出来自A的真实记录。JSON字符串中的\n表示真实换行。

### F2000

文档输入：

```text
Extract the final total and currency. Return only JSON with string keys total and currency.
Document:
Invoice F2000
Currency: USD
Subtotal: 475.34
Tax: 6.62
Total: 481.96
Answer:

```

参考：`{"total": "481.96", "currency": "USD"}`

Base原始生成：

```json
"\n```\n\n```\n\n```\n\n```\n\n```\n\n```\n\n```\n\n```\n\n```\n\n```\n\n```"
```

A训练后原始生成：

```text
{"total":"481.96","currency":"USD"}
```

解释：循环生成代码围栏，没有JSON；属于格式与终止失败。

### F2001

文档输入：

```text
Extract the final total and currency. Return only JSON with string keys total and currency.
Document:
Receipt F2001 | Subtotal 670.65 | Tax 6.76 | Total 677.41 EUR
Answer:

```

参考：`{"total": "677.41", "currency": "EUR"}`

Base原始生成：

```json
"Total: 677.41 EUR\n\n### Subtotal 677.41 EUR\n\nSubtotal 677."
```

A训练后原始生成：

```text
{"total":"677.41","currency":"EUR"}
```

解释：包含正确金额和币种，但继续生成标题；严格协议下仍然失败。

### F2002

文档输入：

```text
Extract the final total and currency. Return only JSON with string keys total and currency.
Document:
BILL F2002
Tax = 27.47
Final total = 608.39 GBP
Subtotal = 580.92
Answer:

```

参考：`{"total": "608.39", "currency": "GBP"}`

Base原始生成：

```json
"Total = 608.39 GBP\n\n### 1.2.2.2.1.1.1.1.2"
```

A训练后原始生成：

```text
{"total":"608.39","currency":"GBP"}
```

解释：出现正确金额与币种后继续生成编号；不能据此说base完全没有字段信息。

## 证据位置

- A：[metadata](runs/run-a-20261111T071605Z/metadata.json)、[配置](runs/run-a-20261111T071605Z/config.json)、[训练逐步日志](runs/run-a-20261111T071605Z/training.jsonl)、[base逐条预测](runs/run-a-20261111T071605Z/baseline-predictions.json)、[训练后逐条预测](runs/run-a-20261111T071605Z/after-predictions.json)、[对比](runs/run-a-20261111T071605Z/comparison.json)、[adapter](runs/run-a-20261111T071605Z/adapter/)、[重加载预测](runs/run-a-20261111T071605Z/reloaded-predictions.json)。
- B：[metadata](runs/run-b-20261111T072140Z/metadata.json)、[配置](runs/run-b-20261111T072140Z/config.json)、[训练逐步日志](runs/run-b-20261111T072140Z/training.jsonl)、[base逐条预测](runs/run-b-20261111T072140Z/baseline-predictions.json)、[训练后逐条预测](runs/run-b-20261111T072140Z/after-predictions.json)、[对比](runs/run-b-20261111T072140Z/comparison.json)、[adapter](runs/run-b-20261111T072140Z/adapter/)、[重加载预测](runs/run-b-20261111T072140Z/reloaded-predictions.json)。

[跨run核验](evidence/run-comparison-audit.json)、[数据审计](evidence/data-audit.json)、[指标测试](evidence/metric-tests.txt)、[Week07冻结验证](evidence/week07-freeze-verification.txt)。`evidence/artifact-manifest.json`记录两个run所有文件哈希，运行快照留存了训练前计划与源码。

## 限制、判断与下一步

1. 只有96条训练与12条验证、3种模板，一次seed；没有置信区间、独立新模板评测或真人账单测试，满分只覆盖这12条。
2. 模板与币种完全相关，存在模板记忆捷径；train/validation的total数值无精确重合，仍不足以证明稳健抽取。冻结v1不修改，后续可另建模板×币种独立组合的开发数据验证。
3. 无扫描、OCR错误、中文、复杂表格、缺字段或多total；不具备视觉输入，不能代替Week07 PDF解析指标。预留12条test本周未做模型评价；Week07 test未参与训练或超参选择。
4. baseline为零主要暴露输出格式问题；已有正确字段片段的样例表明，不应把100个百分点变化描述成全部知识由LoRA学得。
5. 当前Ubuntu环境真实运行与adapter重加载已核验；全新机器安装/完整重训尚未独立验证。seed不保证跨设备版本逐位一致。
6. 本周决定：两份adapter均保留为教学产物，不选为生产模型、不替换Docling。第9周先接入W&B追踪配置、数据版本、训练曲线与adapter；泛化问题需要新增开发集与预先固定协议。

AI使用：Codex生成数据/代码、执行训练、自动核验并撰写报告；本人阅读、抽样核验、实际学习时长与自主阶段尚待完成，见[本人收尾清单](reports/manual-review.md)。
