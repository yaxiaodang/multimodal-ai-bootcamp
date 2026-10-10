# Week 04｜视觉语言模型

本周主线与自主探索已运行完成，当前 CPU 缓存复现成功。最终报告见 [report.md](reports/report.md)，评价采用“任务答案正确性”和“解释忠实性”两个维度。已保存到本地 Git 分支 codex/week04-vlm，GitHub 推送等待认证；全新环境复现未验证。

## 目录与文件

| 位置 | 作用 |
| --- | --- |
| `scripts/` | 可运行程序：准备样例、查模型、单图推理、批量对照、证据核验、刷新报告及评价整理 |
| `configs/` | 模型版本、单图/两组/四组配置，以及样例清单与参考答案 |
| `samples/` | 十张图片和 README 来源说明 |
| `runs/` | 每轮原始配置与回答，按运行时间分目录 |
| `evidence/environment/` | 合并的系统信息与不同阶段依赖快照 |
| `evidence/logs/` | 原始终端运行日志 |
| `evidence/checks.txt` | 合并的依赖、访问与输入检查记录 |
| `reports/` | 最终报告、双维度评价、指标、失败案例、运行表、完整 Prompt、AI 披露及历史过程 |
| `requirements-cpu.txt` | 固定 CPU 版 PyTorch/Torchvision |
| `requirements.txt` | 固定 Transformers 等直接依赖 |

## 程序作用

- `prepare_samples.py`：生成十张自制图，写入 configs/sample-manifest.json 和 samples/README.md；已合并原单图生成程序。
- `check_model.py`：查询固定模型 revision 与许可，保存 configs/model-selection.json。
- `run_single.py`：首次单图验证，可联网下载模型至用户缓存。
- `run_experiment.py`：统一对照入口，一次加载模型，每张图按配置各组生成回答；打印完整 Prompt。
- `verify_evidence.py`：核验每轮回答完整性、图片哈希和 Prompt；未完成运行单独报告。
- `build_reports.py`：刷新 runs.md 与 prompts.md，不覆盖评价。
- `review_results.py`：按已核验的四组历史运行整理评价，不是通用自动评分器；review.csv 已存在时拒绝覆盖。

## 现有环境运行

以下命令都从仓库根目录执行：

```bash
source .venv/bin/activate
set -o pipefail
python -u week04/scripts/run_experiment.py --config experiment-config-factors.json
```

作用：激活环境、保留管道失败状态、运行全部十张图四组实验。`--config` 参数填写 configs 内文件名；添加 `--sample arithmetic` 只运行算术图，添加 `--prepare-only` 只检查输入，不运行模型。默认无 --config 时使用原始两组 32 token 配置；完整自主探索请明确指定 factors 配置。

所有生成参数与完整模板见 configs，四十条实际文本计划见 [prompts.md](reports/prompts.md)。模型与 processor 均固定同一 revision。CPU/float32、4 线程、seed 42、关闭随机采样、非思考模式，四组实验上限 128 token。参考答案不传入模型，每组独立用户消息，不共享上一组回答。

新的批量运行自动创建 `runs/paired-时间/`，其中 `run-metadata.json` 保存版本、配置、状态与运行上下文，`predictions.jsonl` 每行保存一条完整 Prompt、原始答案、输入哈希和耗时，`review.csv` 为新运行的待评价表。历史空白评价副本已删除，最终评价集中在 reports/review.csv。阅读 JSONL 时以 sample_id/variant 找到所需记录。单图历史仍保留 result.json 和 answer.txt。

## 安装与缓存

新环境安装步骤（尚未完整实测）：

```bash
python3 -m venv .venv-week04
source .venv-week04/bin/activate
python -m pip install -r week04/requirements-cpu.txt
python -m pip install -r week04/requirements.txt
python -m pip check
python week04/scripts/check_model.py
python week04/scripts/prepare_samples.py
python -u week04/scripts/run_single.py
```

依次创建环境、激活、安装 CPU 模型依赖、安装推理依赖、检查冲突、核对模型版本、生成输入、首次单图填充模型缓存。样例生成还需 Ubuntu 系统 DejaVuSans 字体。完整历史依赖快照见 evidence/environment/environment-freeze-final.txt；间接依赖未在直接安装清单逐一锁定。

主线 run_experiment.py 使用 local_files_only=True，需事先缓存模型；run_single.py 可首次联网下载。模型权重与虚拟环境不提交 Git。缺少 torchvision 的首次错误已修复；CPU 优化内核回退警告未导致已记录运行失败。

## 核验与成果

```bash
python week04/scripts/verify_evidence.py
python week04/scripts/build_reports.py
```

分别核对原始证据和刷新报告索引。当前 90 条历史配对回答已验证，另有无回答的未完成运行保留元数据。缓存复现四组完整答案、Prompt、哈希、token 数与首次算术四组实验一致；这不等于跨机器复现。

报告文件：report.md 为最终结论；review.csv 为逐项双维度评价与用户备注；metrics.json 为评价计数；failures.md 为五个不同输入案例；runs.md 为证据索引；prompts.md 为完整实际 Prompt；ai-use.md 为 AI 协作披露；history.md 合并阶段分析与旧实验说明。历史阶段待办不表示当前状态，当前状态以本 README 和最终报告为准。

用户已核对五张关键图的参考事实和评价规则；标签由 Codex 依据证据整理，不写作用户逐条签署四十条评价。结论限于十张教学图片，不能视作模型总体准确率或内部推理机制的证明。
