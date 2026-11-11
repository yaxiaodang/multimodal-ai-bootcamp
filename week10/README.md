# Week10｜统一评测、消融与错误分析

本周要学会回答：**效果变化是否来自方法？证据是否足以采用它？** 先读本页理解整体逻辑，再读[实测报告](reports/evaluation-report.md)，最后做[本人收尾](reports/manual-review.md)。

```text
检查任务是否一致 → 冻结数据、指标、变量和决策规则
     ├─ Week07：24页PDF → Docling原基线 / 关闭OCR → 内容、顺序、表格
     └─ Week09：base / A / B → 12条reserved-test → JSON字段严格正确
                       ↓
原始输出 → 总体/切片/资源 → 消融表 → 全部错误候选 → 本人抽样复核
                       ↓
分别判断：保留OCR；文本模型证据有限，暂不生产采用
```

两个分支各自使用同样输入和评分，**分支之间不做跨任务排名**。Week07中文PDF和Week09英文账单模型任务不同，因此课程原设想的“Week09模型直接评Week07 test”在本仓库不适用，明确保留该项差距。没有将PDF参考答案作为模型输入，也没有重新命名旧验证集充当新测试。

## 本周概念只需理解到这里

| 概念 | 本实验里的含义 |
| --- | --- |
| 统一评测 | 同一任务内输入、模型版本、生成方式、指标和失败计分一致 |
| 消融 | 只关掉OCR，观察变化；或在同一基础模型上关闭/启用已训练adapter |
| 分组指标 | 按数字PDF/扫描/表格、布局、扫描质量、文本模板分别看，防止平均数掩盖退化 |
| 错误taxonomy | 给实际错误标出症状，关联原始文件；自动分类并不等于人工确认的原因 |
| 成本 | 同时报实际耗时、可用内存记录、GPU与云费用；加载时间与推理时间区分 |
| 配对bootstrap | 每次对相同文档索引重采样，观察两种方法的差值区间；小合成集不能证明真实泛化 |
| 模型选择 | 综合证据、负面结果和适用边界决定是否采用；高分本身不足以支持部署 |

## 文件作用

| 文件 | 作用 |
| --- | --- |
| [experiment-plan.md](experiment-plan.md)、[协议](configs/protocol.json) | 先固定任务边界、哈希、变量、资源与判断方式 |
| [run.py](run.py) | 唯一实验调度入口，分进程推理、保存日志，不训练 |
| [common.py](scripts/common.py) | 复用Week07/08评分，认证冻结输入和原始结果 |
| [evaluate_text.py](scripts/evaluate_text.py) | 加载固定base或adapter，保存预留测试的每条真实预测 |
| [build_report.py](scripts/build_report.py) | 重算指标、分组、差值区间，生成报告、图表和所有错误 |
| [verify.py](scripts/verify.py) | 不加载模型，复算评分并核对证据哈希 |
| [runs/](runs/) | 原始PDF/文本输出、执行参数、版本、模型身份与资源记录 |
| [错误表](reports/error-taxonomy.md)、[复核CSV](reports/manual-review.csv) | 逐例回到输入、参考及预测；人工栏待本人填写 |
| [AI披露](evidence/ai-usage.md) | 区分AI执行、自动核验与本人人工复核 |

## 在VS Code Remote SSH中复现

所有命令在**Ubuntu远端终端**执行。打开Markdown文件后可用VS Code预览（Ctrl+Shift+V）看表格、图和链接，无需GUI服务器或端口转发。

```bash
cd ~/multimodal-ai-bootcamp
```

作用：进入仓库根目录，以下相对路径以此为基准。

```bash
python3 week10/run.py --verify-only
python3 week10/scripts/test_metrics.py
python3 week10/scripts/verify.py
```

作用：依次核对冻结输入与单变量配置、运行可手算的评分边界测试、核对已归档结果并重新评分。均只需Python标准库，不加载模型、不联网；最后一条生成自动核验JSON，不替代人工复核。

```bash
.venv-week08/bin/python week10/run.py
```

作用：重新执行24页无OCR消融，再用base/A/B在12条预留测试上推理；新建时间戳suite并保存日志。无OCR扫描页可能以空输出失败，原样计0。PDF底层子进程最终退出1是保留质量失败的信号，调度核对24页完整后继续；缺页、未结束、文本推理异常则停止。运行结束打印suite目录，用该目录下的suite.json替换下方路径即可生成新报告。不会重新训练模型。

已归档这次运行的报告重建命令：

```bash
MPLCONFIGDIR=/tmp/bootcamp-week10-mpl .venv-week08/bin/python week10/scripts/build_report.py --suite week10/runs/suite-20261111T080142898866Z/suite.json
```

作用：从明确指定的运行记录重算两个任务的结果、bootstrap、所有错误，生成PNG与Markdown报告和证据manifest。MPLCONFIGDIR让绘图缓存写入临时目录。此命令会更新派生报告和manifest；人工复核CSV已存在时保留，若换suite请另存旧复核表后重新建表，避免混用不同case。

若只复用已完成的本周PDF运行，可在run.py后加 `--pdf-run week10/runs/pdf/baseline-20261111T160020-0f4498`：作用是跳过PDF解析，仅新建文本评测，仍核对24页已处理完毕。分析历史报告无需重复推理。

## 环境、数据与许可

当前VM已有`.venv-week06`（Docling）与`.venv-week08`（训练/推理/绘图）。不安装新库；依赖固定版本及模型准备步骤分别见[Week06](../week06/README.md)、[Week09](../week09/README.md)。新clone先按这两周建立环境并下载固定revision模型；本周没有从空VM重新安装验证。基础模型缓存不提交GitHub，PDF、参考、预测和小adapter可从仓库取回。

PDF：自制虚构CC0-1.0数据，来源/限制见[Week07 Dataset Card](../week07/dataset-card.md)。英文账单：自制虚构数据，见[Week08 Dataset Card](../week08/dataset-card.md)。不含真实隐私；SmolLM2固定revision与Apache-2.0许可继承Week08模型记录；Docling组件许可与来源继承Week06模型准备证据。哈希只能排除精确重复，模板共享仍是泛化限制。本轮测试已经消费，后续调参需要新的最终测试。

## 课程要求与当前状态

| 要求 | 交付/边界 |
| --- | --- |
| Week07 test统一baseline与Week09 runs | PDF在Week07 test统一评；Week09在独立reserved-test统一评，跨任务字面项未完成 |
| 单变量消融 | PDF只关OCR；base/adapter及A/B学习率对照 |
| 总体、分组和成本 | 报告、comparison.json、图及原始metadata；PDF峰值内存未测 |
| 至少20错误与人工复核 | 保留所有真实错误case及唯一文档数；自动taxonomy已生成，人工复核待本人 |
| 正面/负面/限制/采用决定 | 报告明确给出，并区分事实、解释和推测 |
| Week09–10追踪标识 | 保留训练W&B project/run与本地artifact；云版本和Report链接待本人登录 |

## 官方材料与学习顺序

1. [课程Week10](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-10)：先看要留下什么证据。
2. [scikit-learn模型评测](https://scikit-learn.org/stable/modules/model_evaluation.html)：理解选择与任务目标对应的指标，多个指标共同解释表现。
3. [Hugging Face Evaluate](https://huggingface.co/docs/evaluate/index)：理解指标可封装复用；本周复用已冻结的本地指标，不为换库改变定义。
4. [自主学习记录模板](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/11_Learning_Log_Template/)：根目录按字段追加Week10；实际学习时间和个人理解待你填写。
