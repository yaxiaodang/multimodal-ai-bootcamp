# Week08｜LoRA/PEFT 小规模微调

本周要回答：**有限算力下，如何训练一个可复现、有前后对比、能够如实解释限制的adapter？**

先读本页，再读 [真实实验报告](training-report.md)，最后按 [本人收尾清单](reports/manual-review.md) 核验。学习记录追加在根目录 [learning-log.md](../learning-log.md)。

## 主线与整体逻辑

```text
虚构账单文本 → 冻结96 train / 12 validation / 12 reserved-test
                      ↓
135M原始模型 → 同一12条validation生成 → 先保存baseline
                      ↓
冻结base权重 + 添加LoRA → 只学习答案部分 → 固定训练60步
                      ↓
保存adapter → 同一验证集/Prompt/greedy解码 → 前后指标及失败分析
                      ↓
重新加载adapter核对预测 → 只改学习率再跑一次 → 谨慎解释结论
```

这是CPU上的**文本字段抽取SFT**，可视为文档解析后的下游任务。不是多模态视觉微调，不训练Docling；Week07冻结PDF测试集保持独立。课程允许资源不足时用小模型缩小范围；本轮选SmolLM2-135M英语base model，许可Apache-2.0，模型版本固定。账单文字要求输出 `{"total":"123.45","currency":"USD"}`。这个小任务也能用规则解决，LoRA在这里用于学习研究流程，未证明它比规则更合适。

SFT是用“输入→参考答案”示范训练；PEFT是一类只训练少量参数的方法；LoRA通过两个较小矩阵学习权重增量，可写成 `W_new = W_frozen + (alpha/r) × B × A`。本实验冻结原始模型，在注意力的q_proj/v_proj加入LoRA，只保存增量权重；推理仍需相同base及tokenizer。它能减少训练参数与优化器状态，前向/反向仍需经过base，不意味着无需算力或显存。

## 本周完成项与文件作用

| 证据 | 作用 |
| --- | --- |
| [训练前计划](post-training-plan.md) | 先定义假设、协议、预算、成功与停止条件 |
| [数据卡](dataset-card.md)、[冻结清单](data/freeze.json) | 交代来源、许可、split、偏差与哈希 |
| [配置A](configs/run-a.json)、[配置B](configs/run-b.json) | 固定所有训练选项，B仅学习率不同 |
| [train.py](train.py) | 数据校验→baseline→LoRA→保存→同集评测→重加载核对 |
| [prepare_data.py](scripts/prepare_data.py) | 一次生成合成账单和参考，不覆写冻结集 |
| [重算指标](scripts/recompute_metrics.py) | 从原始预测重算JSON/字段指标，无需加载模型 |
| [训练报告](training-report.md)、[runs/](runs/) | 前后对比、日志、adapter、资源、失败证据和快照 |
| [依赖快照](requirements-lock.txt) | 当前完整环境的pip freeze；包含复用环境中的非必要包 |
| [例会讲解](reports/meeting-notes.md)、[本人收尾](reports/manual-review.md) | 概念讲解、证据展示与本人待核验项 |

## 只需理解的参数

| 配置 | 本轮设置与含义 |
| --- | --- |
| r / alpha | 8 / 16，低秩矩阵容量和缩放，alpha/r=2；本周未搜索rank |
| target_modules | q_proj、v_proj，只在这些注意力投影中加入可训练增量 |
| learning_rate | A=0.001，B=0.0005，每次更新幅度；唯一探索变量 |
| batch / accumulation | 每小批2条，积累2次才更新，有效batch=4 |
| max_steps | 60次优化器更新，约240条次、2.5轮训练数据，不按最好验证结果挑checkpoint |
| precision / optimizer | CPU FP32 / AdamW，无量化、无GPU训练 |
| seed | 42，固定初始化与数据顺序；不保证跨版本硬件逐位相同 |
| loss | 只在答案与EOS上计算；Prompt及padding不计入训练loss |

生成质量主指标是**严格JSON解析后的两个字段完全正确率**，要求字符串值与参考一致，额外字段也算失败；不要求JSON键排列或空格相同。辅助为可解析率、字段准确率及答案token平均NLL。NLL下降意味着参考答案更可能，不保证模型自由生成正确。验证集只12条，一条就影响8.33个百分点，不能宣称统计稳定提升。

## 当前Ubuntu虚拟机：在VS Code Remote SSH终端操作

首次真实运行已由Codex代执行，阅读报告不需重新训练。

```bash
cd ~/multimodal-ai-bootcamp
```

作用：进入仓库根目录，统一所有相对路径。

```bash
.venv-week08/bin/python week08/train.py --verify-only
```

作用：检查冻结数据与生成器哈希，不加载模型、不训练、不修改结果。

```bash
.venv-week08/bin/python week08/scripts/test_metrics.py
```

作用：检查手算JSON评分与数据篡改拒绝机制，不运行模型。

```bash
HF_HUB_OFFLINE=1 .venv-week08/bin/python week08/train.py --config week08/configs/run-a.json
```

作用：使用本地固定模型缓存，完成A的baseline、60步训练、评测与adapter重加载，创建带时间戳的新目录；预计数分钟，训练上限15分钟。只改配置路径为 `week08/configs/run-b.json` 可运行B。`HF_HUB_OFFLINE=1`关闭Hub联网探测，不影响训练算法。已有目录不会覆盖；失败时保留failure.json与日志并返回非零码。模型下载必须先完成。

报告中有首次真实run目录。重算指标时将以下占位路径换成报告里的完整目录名：

```bash
.venv-week08/bin/python week08/scripts/recompute_metrics.py --run week08/runs/报告中的目录名
```

作用：读取baseline/after/reloaded原始预测，重算四项任务指标并与保存值比较；不重算需要模型的NLL，不需要GPU或联网。

## 全新Ubuntu环境：安装与下载

当前环境为Python3.10，专用venv通过.pth复用既有PyTorch以节省磁盘，详情见 [准备记录](evidence/setup-notes.md)。其他机器无需复制这个本机路径，使用独立环境：

```bash
python3.10 -m venv .venv-week08
```

作用：用Python3.10创建隔离环境；不要误用系统Python3.14后混入3.10扩展。

```bash
.venv-week08/bin/python -m pip install 'torch==2.14.0' --index-url https://download.pytorch.org/whl/cpu
.venv-week08/bin/python -m pip install -r week08/requirements.txt
```

作用：第一条安装CPU版PyTorch，第二条安装固定版本的Transformers、PEFT等训练组件。无需CUDA或付费服务；依赖下载需要联网。完整环境快照用于审计；新机器独立安装流程尚未实测。

```bash
.venv-week08/bin/python week08/scripts/download_model.py
```

作用：从Hugging Face下载固定revision的公开模型、tokenizer和模型卡到 `.cache-week08/hub`，约260MiB文件，不上传数据，不需要账号密钥。之后使用前面的A训练命令即可。

数据与参考已提交，无需重建。`prepare_data.py`仅说明来源；已有freeze时会拒绝覆盖v1。普通终端若代理不可用，应先检查Ubuntu自己的网络配置。

## 官方阅读顺序

1. [第8周课程](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-8lorapeft)：核对baseline、adapter与公平对比要求。
2. [模型卡](https://huggingface.co/HuggingFaceTB/SmolLM2-135M)：确认它是英语文本base及使用限制。
3. [PEFT Quicktour](https://huggingface.co/docs/peft/quicktour)：理解“只训练adapter”和保存/加载。
4. [LoRA参数](https://huggingface.co/docs/peft/package_reference/lora)：只关注r、alpha、target_modules；[PyTorch复现说明](https://docs.pytorch.org/docs/stable/notes/randomness.html)用于理解seed边界。

AI使用披露：Codex撰写代码、准备计划、生成数据、执行实验与自动核验、整理报告；本人尚需完成阅读、抽查、实际时长与自评。W&B接入安排在第9周，本周不要求登录W&B，也不创建云端训练。
