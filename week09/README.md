# Week09｜W&B 实验追踪

本周核心问题：**怎样让一次结论能回查到配置、原始结果、数据、代码和adapter？**

先看本页理解主线，再看[实测报告](reports/report.md)和图表，最后完成[本人收尾清单](reports/manual-review.md)。根目录[学习记录](../learning-log.md)按课程模板追加，实际学习时间和人工核验尚待本人填写。

## 本周主线与整体逻辑

```text
Week08固定数据、模型revision和训练协议
        ↓
训练入口创建W&B run：记录身份、完整配置、源码commit/哈希
        ↓
先保存base预测 → LoRA训练每一步log loss/lr/内存/耗时
        ↓
相同validation生成 → 保存adapter → 重加载核对预测
        ↓
dataset/code/model/evaluation artifacts关联本次run
        ↓
A/B仅改学习率 → 比较图表、负面结果 → 形成报告和模型选择判断
        ↓
本机离线记录 → 本人登录后sync → 云端artifact版本和W&B Report
```

这里不需要重新学习LoRA内部实现。沿用Week08的CPU文本账单字段抽取SFT，主指标是JSON两个字段严格完全正确率，验证集12条，不把它说成视觉微调或真实文档benchmark。A/B都是新训练，从同一基础模型开始；只改变学习率0.001/0.0005，配置中的name仅用于标识。数据96 train/12 validation/12 reserved-test，reserved-test只核对哈希，不读取内容进行训练或调参。

| 概念 | 在本实验的作用 |
| --- | --- |
| project / run | project组织相关实验；一个run对应一次独立执行，有唯一ID |
| config | 描述“怎么跑”：模型revision、seed、数据哈希、学习率等 |
| history / summary | history保存随步骤变化的曲线；summary保存最终指标与状态 |
| system metrics | 观察资源：SDK系统采样，加上每步显式记录的RSS、CPU与耗时 |
| artifact | 有版本的文件集合，把数据、代码、adapter、评测结果与run关联 |
| Report | 将图表、结论、负面结果与下一步组织成可读的W&B网页报告 |
| offline / sync | 先用真实SDK写本机记录，后续同步到云端；离线ID不等于云端已存在 |

## 已执行与当前边界

已完成：接入W&B、真实A/B训练、配置diff、训练曲线、任务指标、资源记录、artifact本地digest/文件SHA256、重加载核对、失败演练、报告草稿与自动核验。详细数字以[报告](reports/report.md)和[核验JSON](evidence/verification.json)为准。

尚未完成：W&B账号登录、云端同步、artifact `:vN`、网页Report URL、本人人工抽查与学习时间。当前没有W&B凭据，没有编造云端链接，也没有开通付费云算力。

## 与课程任务逐项对应

| 课程要求 | 本次交付与状态 |
| --- | --- |
| Week08代码接入W&B | 可选追踪参数，真实离线SDK，未保存密钥 |
| 至少两个单变量runs | A/B仅改learning_rate，原始配置与diff可查 |
| config/metrics/system/time | 完整config、每步history、最终summary、SDK原生系统采样 |
| 数据/adapter/代码commit关联 | 四类artifact、digest、文件SHA256、源码快照和run ID |
| W&B Report | 本地正文、图表和负面结果已准备；网页创建与实际链接待本人 |
| 自主探索：追踪 | 从报告回查到run → Git/源码哈希 → 数据版本 → adapter；额外验证中断留痕 |

## 文件和代码只需理解到这里

| 文件 | 作用 |
| --- | --- |
| [运行前计划](experiment-plan.md) | 先定变量、数据、指标、资源上限、失败恢复和模型选择规则 |
| [week08/train.py](../week08/train.py) | 原训练入口，可选启用追踪；不加新参数仍按Week08方式运行 |
| [tracking.py](tracking.py) | 负责init、log、summary、artifact和JSON导出，不改变训练算法 |
| [run.py](run.py) | 顺序运行A、B和第2步主动中断演练，保存完整日志与退出码 |
| [configs/](configs/) | A/B冻结配置，唯一算法差异为learning_rate |
| [runs/](runs/) | 每次执行的配置、预测、训练日志、adapter、身份和产物清单 |
| [verify.py](scripts/verify.py) | 从原始预测重算指标、检查单变量、文件哈希和W&B原生记录 |
| [build_report.py](scripts/build_report.py) | 从实测数据生成图表与报告，不生成模拟实验数字 |
| [sync_cloud.py](scripts/sync_cloud.py) | 登录后同步指定runs，再从API读回真实链接和artifact版本 |
| [AI使用与核验](evidence/ai-usage.md) | 说明AI代执行、修复的错误与本人人工核验边界 |
| [meeting-notes.md](reports/meeting-notes.md) | 几分钟说明实验主线、证据、限制 |

## 当前Ubuntu VM：VS Code Remote SSH终端

以下命令都在**远端Ubuntu终端**执行。当前环境已安装所需依赖和固定模型缓存，无需重新安装或训练也能读报告。

```bash
cd ~/multimodal-ai-bootcamp
```

作用：进入仓库根目录，确保相对路径正确。

```bash
.venv-week08/bin/python week09/scripts/verify.py
```

作用：校验冻结数据、配置唯一差异、原始预测评分、adapter重加载一致性、artifact每个文件的SHA256，以及真实W&B二进制记录中的history/system stats/artifact/退出码；不加载模型、不联网。新clone没有原生spool时先用下一条运行命令生成。

```bash
.venv-week08/bin/python week09/run.py
```

作用：从头运行两个60步CPU LoRA实验和一个第2步中断演练，创建新的时间戳目录与W&B ID，保留日志，不覆盖旧结果。脚本为子进程设置HF_HUB_OFFLINE=1，只使用已缓存模型；每个训练循环上限900秒。离线W&B仍需要本机socket，普通Ubuntu SSH终端一般可直接运行，Codex沙箱需相应执行权限。演练子进程返回1是预期行为，调度脚本核对后继续完成。

```bash
MPLCONFIGDIR=/tmp/bootcamp-week09-mpl .venv-week08/bin/python week09/scripts/build_report.py
```

作用：从完成的run读取原始训练曲线、指标和耗时，重新生成图与本地报告；环境变量把Matplotlib字体缓存放到可写临时目录。此步骤会更新reports中的派生文件。图表横轴optimizer step，NLL图使用对数纵轴。

登录、上传和Report的实际步骤集中在[本人收尾](reports/manual-review.md)，本机spool位于 `week09/wandb/wandb/offline-run-*`，同步前保留 `.cache-week09/`。这些本机文件不提交Git，JSON导出和小adapter提交GitHub。新clone能够审查导出，但要运行新实验才能获得可同步spool，旧ID不能靠JSON重建。

## 全新Ubuntu环境

```bash
python3.10 -m venv .venv-week08
```

作用：创建Python3.10虚拟环境。当前VM复用了既有PyTorch安装；其他机器使用独立安装，不复制本机.pth。

```bash
.venv-week08/bin/python -m pip install 'torch==2.14.0' --index-url https://download.pytorch.org/whl/cpu
.venv-week08/bin/python -m pip install -r week09/requirements.txt
```

作用：第一条安装CPU PyTorch；第二条安装冻结的训练、W&B、绘图与资源监测依赖。完整实际环境见[lock](requirements-lock.txt)，新机器安装流程未独立实测。下载公开包需要联网。

```bash
.venv-week08/bin/python week08/scripts/download_model.py
```

作用：从Hugging Face下载固定revision的公开135M基础模型及tokenizer，约260MiB；不上传输入。然后执行上面的Week09运行入口。

## 学习材料与核验顺序

1. [课程Week09](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-9wb)：核对runs、artifact、Report三类交付。
2. [课程Stage 3](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/08_Post_Training/#stage-3-weights-biases)：理解身份、训练、任务指标、资源和异常记录。
3. [W&B Quickstart官方源文档](https://github.com/wandb/docs/blob/main/models/quickstart.mdx)、[summary官方源文档](https://github.com/wandb/docs/blob/main/models/track/log/log-summary.mdx)：理解config/log/summary。
4. [Artifacts官方源文档](https://github.com/wandb/docs/blob/main/models/artifacts/construct-an-artifact.mdx)、[sync官方源文档](https://github.com/wandb/docs/blob/main/models/ref/cli/wandb-sync.mdx)：理解文件集合、离线后同步、版本号。课程官方链接部分发生重定向，核对时使用了W&B官方docs仓库和已安装SDK0.31.0的CLI/API。
5. [创建Report官方源文档](https://github.com/wandb/docs/blob/main/models/reports/create-a-report.mdx)：从Workspace选择图表或Reports入口建立报告，固定A/B run集合。
6. [学习记录模板](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/11_Learning_Log_Template/)：Week09还须记录project/run/artifact/report标识，未知值保持待补。

AI披露：Codex完成代码、实验与自动核验、中文材料；本人阅读和人工核验待完成。不要把自动检查写成人工确认。
