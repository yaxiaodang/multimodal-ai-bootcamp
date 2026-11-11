# Week11｜论文导读与最小复现

本周回答：**论文的一项主张，在现有CPU和项目里能否被部分验证？** 不必逐行理解代码。先读[Paper Card](paper-card.md)，再读[复现报告](reports/reproduction-report.md)，最后做[本人收尾](reports/manual-review.md)。

```text
LoRA原论文/作者代码 → 区分问题、主张、证据、限制
                 ↓
事前计划与Git提交 → 固定输入、标准、预算（不是盲法研究）
                 ↓
96条训练文本 + 固定base → r4 / r8新训练（仅rank配置改变）
                 ↓
12条validation：训练前 / 训练后 / 重加载 / 合并后
                 ↓
严格JSON评分 + 基座哈希 + delta公式 + logits一致性
                 ↓
解释本地与论文差异 → 保留失败/限制 → 本人抽查与五句话分享
```

这是文档文字字段抽取的**机制复现及迁移验证**。它承接Week08/09，不能代替视觉模型或Docling的PDF实验，也不把Week10已用过的test重新当作未见测试。

## 只需掌握的实现逻辑

| 概念/文件 | 作用 |
| --- | --- |
| LoRA | 保持大模型原权重，另学两个小矩阵A/B；r控制矩阵中间维度，主要参数数目随r增加 |
| `W = W₀ + (α/r)BA` | 训练时通过小支路修正输出；合并时把这份修正加进原权重 |
| 基座冻结 | 非LoRA权重训练前后哈希相等；既检查可训练名单，也检查真正的权重值 |
| 重新加载 | 确认保存的adapter能够恢复训练后的结果 |
| 合并检查 | 确认去掉小支路后仍保持数值与预测；本周没有测推理加速 |
| [run.py](run.py) | 唯一调度入口：先核验计划/输入，再按顺序训练、验证和生成报告 |
| [Week08 train.py](../week08/train.py) | 复用已审计训练代码，先保存baseline，只训练A/B，保存逐步loss与小adapter |
| [check_mechanism.py](scripts/check_mechanism.py) | 从真实adapter检查零初始化、60层delta公式、合并前后12个Prompt的logits和生成 |
| [build_report.py](scripts/build_report.py) | 用明确suite重建指标表、案例与报告，不修改原始预测 |
| [verify.py](scripts/verify.py) | 不加载模型，核对归档哈希、配置、60步完整性与原始预测评分 |
| [计划](experiment-plan.md)、[配置](configs/) | 在新训练之前固定本地主张、标准和停止条件 |
| [runs/](runs/)、[证据](evidence/) | 保存真实运行、源码/计划快照、预测、日志、adapter和验证记录 |

## Ubuntu + VS Code Remote SSH操作

在VS Code连接虚拟机后，打开**Ubuntu远端终端**。本周不需要开网页服务、配置端口转发或提供API key。Ctrl+Shift+V可预览Markdown。

```bash
cd ~/multimodal-ai-bootcamp
```

作用：进入仓库根目录，后续命令从这里执行。当前成果已代运行，学习报告无需重训。

```bash
python3 week11/run.py --verify-only
python3 week11/run.py --check-archive
```

作用：第一条核对冻结数据、两组配置差异并打印输入SHA；第二条核对已归档文件并从原始预测重算指标。只用Python标准库，不联网、不加载模型、不训练；归档核验输出到`week11/evidence/verification.json`。自动核验不代替本人理解或人工抽查。

```bash
.venv-week08/bin/python week11/run.py
```

作用：使用已有CPU环境，先确认计划/可执行输入已提交Git，再依次新训练r4/r8（各60步），执行真实模型机制核验，并从新suite生成报告。新建时间戳目录；旧原始运行保留。约需10–15分钟，VM负载会影响时间；训练单run上限900秒、训练脚本上限1200秒，机制核验每run上限300秒。报告会指向新suite；若你新增个人复核，应先把旧复核另存，避免混用case。失败日志原样保留，不为提分自动重跑。

如只重建本次归档报告：

```bash
python3 week11/scripts/build_report.py --suite week11/runs/suite-20261111T081647230916Z/suite.json
python3 week11/run.py --check-archive
```

作用：先从明确suite生成指标表、原始案例与SHA清单，再独立核验原始评分；不加载模型、不训练。第一条会更新派生报告和manifest，原始预测不变。本人复核文件独立保留；换suite需另存旧人工记录，避免把旧判断套在新结果上。

初次clone须先按[Week08环境说明](../week08/README.md)建立Python3.10 CPU环境并下载固定revision的模型。本次沿用现有环境，依赖锁见[Week08](../week08/requirements-lock.txt)，没有再次从空VM安装验证。本周没有额外依赖。模型缓存`.cache-week08/`和虚拟环境不入库，小adapter入库。

归档manifest覆盖本周源码、配置、原始结果与报告；`manual-review.md`作为后续本人填写文件单独列出，不计入冻结SHA。报告重建会更新manifest；原始输入与算法仍须匹配suite的事前快照。

数值核验使用事先固定的`atol=1e-4, rtol=1e-4`：每个值允许的差是`atol + rtol × |比较值|`，因此最大绝对差可能略高于1e-4而仍通过。生成文本另外要求逐条一致，不用浮点容差放宽JSON评分。

## 学习顺序与交付状态

1. 阅读Paper Card，在原文§4.1和§7.2找到主张和边界；核对一次官方`Linear`实现。
2. 阅读事前计划，理解为何使用validation、为何不宣称独立泛化、为何固定停止条件。
3. 看报告的对比表和两个原始案例，沿链接找配置、预测和adapter。
4. 运行两条轻量核验命令，最后按本人收尾清单抽查并填写实际学习时间。

课程要求的Paper Card、事前计划、配置、真实原始运行和复现报告均已整理；一次自主探索选择rank4/8对照。本人独立阅读、抽样复核、学习时间、自评和例会讲解仍待你完成。五句话讲稿见[例会准备](reports/meeting-notes.md)。

## 来源与使用范围

- [课程Week11](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-11)：明确本周证据要求。
- [学习记录模板](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/11_Learning_Log_Template/)：根目录`learning-log.md`按此追加Week11，保留此前各周。
- [LoRA论文v2](https://arxiv.org/html/2106.09685v2)、[官方代码固定版本](https://github.com/microsoft/LoRA/tree/c4593f060e6a368d7bb5af5273b8e42810cdef90)：核对方法和证据；官方代码MIT，本实验未复制或安装loralib。
- [固定模型卡](https://huggingface.co/HuggingFaceTB/SmolLM2-135M/blob/93efa2f097d58c2a74874c7e644dbc9b0cee75a2/README.md)：Apache-2.0；小模型仍有错误输出风险，限教学。
- 数据继承[Week08数据卡](../week08/dataset-card.md)，自制虚构CC0-1.0，无真实隐私；模板与币种相关性、同分布小样本和已使用过的validation均是限制。
- [NeurIPS Checklist](https://neurips.cc/public/guides/PaperChecklist)：借鉴主张/限制/可复现证据自查；[ACM Artifact Review](https://www.acm.org/publications/policies/artifact-review-and-badging-current)仅为课程提供的概念入口（本轮抓取403），未申请或获得任何徽章。

## 课程要求与证据对应

| Week11要求 | 本仓库交付 | 状态/边界 |
| --- | --- | --- |
| 相关论文与可核查代码 | Paper Card、固定arXiv v2、官方代码commit | 已核对；本人阅读待做 |
| 一页Paper Card，区分问题/主张/证据/限制 | [paper-card.md](paper-card.md) | AI已整理 |
| 先固定主张、范围、标准、预算与停止条件 | [计划](experiment-plan.md)、计划提交863c77f | 先提交后运行；已有r8历史知识已披露 |
| 小规模复现与原始结果 | [runs/](runs/)、配置、训练日志、adapter和预测 | CPU真实新训练；无付费云 |
| 论文与本地设置差异 | 报告差异表 | 模型/数据/初始化/实现/对照/重复/测速范围明确 |
| 一次自主探索 | 固定alpha下rank4/8对照 | 不声称纯容量效应或最优rank |
| 五句话分享与个人学习记录 | 例会讲稿、根目录learning-log.md | 本人抽查、实际时间、自评与讲解待做 |
