# 12 周自主学习日志

每周记录实际完成的工作、遇到的问题、解决方法，以及下一步任务。运行结果以仓库中的代码、Notebook 和输出文件为准。

## Week 01：环境与可复现性基础

### 核心问题与路径

- 核心问题：另一位同学能否只根据仓库说明，重建环境并运行图片信息工具？
- 选择标准路径：完成工具、正常与异常输入测试、PR，以及全新 clone 和虚拟环境复现；自主探索选择比较“能运行、可复现、可审计”。

### 主线成果与运行入口

- 建立仓库和 Python 虚拟环境，编写环境检查、样例图片生成及单张图片信息读取工具；项目范围和成功标准见 [项目计划](week01/docs/project_plan.md)。
- 当前版本从仓库根目录创建虚拟环境、安装 [依赖](requirements.txt) 后，执行 `cd week01 && python scripts/create_sample.py && python src/image_info.py samples/demo.png`；完整步骤见 [Week 1 README](week01/README.md)。
- Week 1 当时的三个测试均通过；Week 3 后扩充为九个测试。这两个结果属于不同阶段，不应混作同一次实验。

### 环境与证据索引

| 证据 | 位置与实际记录 |
| --- | --- |
| 版本 | [Week 1 PR #1](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/1)，合并提交 `1fd5128`；随后按周整理目录的提交见 [PR #2](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/2) |
| 环境与依赖 | [环境原始输出](week01/evidence/environment-output.txt)：Ubuntu、Python 3.10.12、CPU；[requirements.txt](requirements.txt) 固定 Pillow 11.3.0 和 pytest 8.4.1 |
| 输入与来源 | [生成脚本](week01/scripts/create_sample.py) 自制 640×480 PNG；不含个人信息或第三方素材；未使用外部数据集，license 和 split 不适用 |
| 配置 | 固定图片尺寸与颜色；没有模型、Prompt 或随机过程，revision、seed 和受控单变量比较不适用 |
| 正常结果 | [原始输出](week01/evidence/success-output.txt)：宽 640、高 480、格式 PNG |
| 错误与测试 | [错误原始输出](week01/evidence/error-output.txt)：文件不存在，退出码 2；[当时测试原始输出](week01/evidence/test-output.txt)：3 passed。这是功能测试结果，不是模型准确率 |
| 独立复现 | [复现记录](week01/docs/reproducibility_notes.md)：2026-09-21 全新 clone 和 venv，以及同伴在 Ubuntu 的运行反馈 |

### 耗时、资源与 AI 使用

- 课程建议标准路径约 24 小时；本人当时的预计/实际耗时及费用没有留下可核对记录，不补写估计值。运行设备为 Ubuntu 虚拟机的 CPU，本周任务不需要 GPU 或云端算力。
- Week 1 当时没有留下完整的 AI 使用与人工核验记录，因此不追溯断言具体参与范围。Week 3 对同一工具的 AI 辅助改动另见 [Week 3 记录](week03/ai-use-log.md)。

### 探索、失败与当前判断

- 自主探索：比较“能运行、可复现、可审计”，说明和证据见 [专题记录](week01/docs/reproducibility_concepts.md)。
- 遇到的问题：文件移动到 `week01/` 后，直接运行 `pytest -q` 曾出现 `ModuleNotFoundError: No module named 'src'`；在 `week01/` 目录改用 `python -m pytest -q` 后通过。
- 自主阶段：就 Week 1 的历史成果而言，依据全新环境和同伴复现记录，判断为 **可复现**；这不表示已经完成跨操作系统验证。
- 结论：虚拟环境、依赖、输入、运行命令、测试及错误输出共同支持复现；周目录用于整理产物，Git 分支用于隔离待合并的修改。
- 限制与未知：工具只处理单张图片，不支持 PDF、OCR 和批量处理；跨操作系统的复现情况仍未知。下一步最小验证是在另一种操作系统上按 README 运行，并记录差异。
- 后续补充：Week 3 扩充测试后，2026-09-28 从 [PR #6](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/6) 的分支新建本地克隆和虚拟环境，得到 9 passed、正常图片输出及错误退出码 2；此次是后续核验，不改写 Week 1 的原始记录。

### 例会前准备

- 展示：图片检查命令与 640×480 PNG 的原始输出。
- 证据：全新环境与同伴复现记录、正常与错误输出、Week 1 PR。
- 最大意外：目录迁移后 `pytest -q` 找不到 `src`；说明运行目录和命令也是复现条件。
- 下一步：检查其他操作系统能否按 README 重建环境，并继续记录失败原因。

## Week 02｜Hugging Face 与模型推理

> 本节区分第一遍的历史实验与第二遍复盘。历史事实依据仓库文件；第二遍未执行的操作保留为待完成，不以已有文件代替本轮核验。

### 本周核心问题

- 我准备回答：如何依据目标任务、Model Card、资源条件和实际输出选择模型，并说明结果与限制？
- 第二遍目标：掌握模型选择 → 固定版本 → 加载与推理 → 保存证据 → 分析失败的主线，为组会汇报准备可核对的解释。

### 时间与任务计划

- 选择路径：标准路径复盘。沿用已有实验，重点核对证据和理解，不增加大模型部署任务。
- 第二遍建议预算（不是实际耗时）：官方材料 1.5 小时；主线梳理与重跑 2 小时；结果与失败分析 1 小时；缓存探索复盘 0.5 小时；记录与例会准备 1 小时；合计 6 小时，可按实际调整。
- 第一遍预计/实际耗时：没有可核对记录；第二遍实际耗时：待记录。

### 本周主线成果

- 第一遍已有产物：固定版本的 DistilBERT CPU 推理、三条正常文本、一条反讽文本、一条无效输入；模型比较、FUNSD 页面调查和离线缓存检查。
- 第二遍尚未完成：核对 Model Card 和比较表；确认当前解释器与内核；重启内核并从头运行；检查配置与新输出一致性；完成口头解释与组会展示。
- 唯一主线运行入口：[transformers-demo.ipynb](week02/transformers-demo.ipynb)。在 VS Code Remote SSH 连接的 Ubuntu 中选择项目 `.venv` 内核，重启内核后运行全部单元；准备步骤见 [README](week02/README.md)。离线探索是单独入口，不等同于主线 Notebook 全部运行成功。
- 算力与成本：历史实验使用 Ubuntu 虚拟机 CPU，CUDA 不可用；本轮沿用 CPU，不计划租用 GPU；历史实际费用未记录。
- 预期/实际文件：主线 Notebook、机器可读配置、原始输出、模型比较与失败分析均已存在；详见下方证据表。本轮是否完成核验另行记录。

### 环境与复现信息

- 本次文档核对的仓库基线 commit：`2beda4db1c39e6762872570b3c07eb56edc4f9a8`。它是当前证据快照，不是第一遍推理运行时的 commit；历史运行 commit 未记录。
- 历史环境记录：Python 3.10.12、PyTorch 2.14.0+cpu、Transformers 5.17.0、huggingface_hub 1.32.0；当前环境需本轮重新核对。
- 实际运行模型：`distilbert/distilbert-base-uncased-finetuned-sst-2-english`；revision：`714eb0fa89d2f80546fda750413ed43d93601a13`；记录的 license：Apache-2.0。
- 推理配置：`text-classification`，`DEVICE = -1`（CPU）；分类任务没有文本生成参数。配置见 [run-metadata.yaml](week02/run-metadata.yaml)。
- 数据来源：Notebook 内的五条手工测试输入；不是从 FUNSD 抽取的评测集。没有 train/test split，也不能计算代表性的总体准确率。
- FUNSD：仅完成页面调查，没有下载或用于推理；数据集 revision、许可核查的缺口见 [dataset-review.md](week02/dataset-review.md)。
- 随机种子：历史实验未记录；本轮先保持固定模型和固定输入，不将 seed 缺失解释为跨环境完全一致的保证。
- 依赖：见 [environment-freeze.txt](week02/environment-freeze.txt)。根目录 `requirements.txt` 仅含 Week 1 依赖，尚不足以独立重建 Week 2 环境。
- 网络：Notebook 含特定代理地址与在线连接检查；重跑前需核对。缓存检查成功不表示断网时主线 Notebook 能从头运行。

### Evidence Manifest 自查

以下复选框表示第二遍核验状态，不能仅凭第一遍存在文件就勾选。

- [ ] 核对测试输入来源、模型许可和隐私状态；说明 FUNSD 未参与推理。
- [ ] 从头重跑，并核对原始输出、配置、环境与文件位置。
- [ ] 记录本轮保持不变的条件、唯一验证项和失败案例；主线不进行跨模型性能比较。
- [ ] 披露本轮 AI 使用，并完成人工核验。
- [ ] 能说明当前结论、限制，以及下一步最小验证。

### 实验记录

| Run | 唯一改动或验证项 | 关键配置 | 历史结果 | 原始证据 |
| --- | --- | --- | --- | --- |
| 正常输入 | 固定模型，依次输入三条文本；属于样例检查 | 固定 revision、CPU、text-classification | 正面、负面、负面 | [predictions.jsonl](week02/predictions.jsonl)：normal_01–03 |
| 反讽探针 | 输入含反讽的文本，不改模型 | 同主线配置 | POSITIVE，score 0.9925507307052612，与人工语境判断不符 | [原始输出](week02/predictions.jsonl)：limitation_01；[失败分析](week02/failure-case.md) |
| 输入类型检查 | 把文本输入改为整数 12345 | 同主线配置 | ValueError；这是接口错误，不是模型误分类 | [原始输出](week02/predictions.jsonl)：invalid_01 |
| 离线缓存检查 | 验证已有缓存能否在离线模式下加载 | 固定 revision、CPU，单独脚本 | 成功加载并输出 POSITIVE | [脚本](week02/offline-cache-check.py)、[原始日志](week02/offline-cache-output.txt) |
| 第二遍主线重跑 | 计划保持模型、配置和五条输入不变，验证顺序执行与记录一致性 | 已确认终端与 Notebook 使用项目 .venv，依赖版本与历史记录一致 | 本轮成功 [本轮输出](week02/evidence/review-20261007/predictions.jsonl)| 待本轮执行后记录；耗时变化不直接视为模型性能变化 |

补充证据：[结果摘要](week02/result.md)、[模型比较](week02/model-comparison.md)、[Hub 基础笔记](week02/huggingface-basics.md)。模型比较表已存在，但参数规模仍有待记录项，资源判断尚需区分资料信息与实测结果。

### AI 使用披露

- 本轮工具：ChatGPT；具体模型版本未单独记录。
- AI 建议：按官方模板整理学习记录、核对仓库证据、设计第二遍复盘顺序。
- 人工核验：待逐项对照仓库文件、官方 Model Card、本机环境和本轮输出；文档整理不等同于实验已经重跑。
- 本轮未采纳的写法：不把历史待办照搬为当前未完成，也不把已有产物写成本轮已完成；避免混淆阶段。
- 第一遍 AI 参与范围未完整记录，不追溯编造。

### 自主探索方向

- 选择：revision 与本地缓存对复现的影响。
- 相关性：固定模型文件和理解下载/缓存，有助于解释首次加载、后续加载与离线运行的区别。
- 只验证：固定版本已缓存时，单独离线脚本能否完成加载和推理。
- 历史结果：检查已成功，见上方日志；第二遍先解释已有证据，不扩展到多个模型的性能实验。

### 自主阶段

- [ ] 未形成：只有阅读或尝试。
- [x] 已跑通：历史原始结果支持最小推理和独立缓存检查成功。
- [ ] 可复现：尚需补足 Week 2 依赖安装说明并核对独立重建；现有环境重跑不等同于全新环境复现。
- [ ] 可解释：本轮目标；待能独立说明选择依据、输入输出、失败和限制后勾选。
- [ ] 可扩展：暂未做跨模型受控实验或系统评测。

### 当前判断

- 最重要的发现：本周学习的是选择与正确使用模型的流程；英文情感分类实验为后续视觉/多模态推理提供工程基础。
- 一个失败：反讽句获得高分正面标签，但与人工判断不一致。score 不是“回答正确率”；仅凭该结果也无法证明模型内部失败机制。
- 排查与恢复：历史网络问题在配置可用代理后恢复；无效输入错误需要调整输入类型，与有效文本上的分类失败分别处理。
- 当前限制：只有少量自选样例；没有总体准确率评测；Qwen 只作资料对比，没有运行，其速度、内存和效果不能作为本次实测结论。
- 我还需理解：Hub 与 Transformers 的分工；ID 与 revision 的区别；pipeline 的输入处理、模型计算和输出整理；分类分数的含义；环境、输入、模型版本如何共同影响复现。
- 下一步最小验证：先确认 SSH 终端、Python 解释器和 Notebook 内核属于同一 Ubuntu 项目环境，再阅读并解释实际模型的任务、输入输出和限制。

### 例会前准备

- 展示成果：一项模型选择决策、一条正常原始输出和一条反讽失败输出。
- 最有说服力的证据：固定 revision、CPU 配置、保存的输入与原始输出；缓存日志作为补充。
- 希望交流：如何避免把分类高分、少量样例成功或文档中的能力描述当成真实任务上的效果保证？
- 复盘后首先完成：将第二遍的环境、运行结果和独立解释补回记录，再进入 Week 3 的人工验证复盘。

### 第二遍复盘记录｜2026-10-07

- 执行方式：确认终端与 Notebook 均使用项目 `.venv`；
  重启 Notebook 内核后，从顶部顺序运行全部单元。
- 环境：Python 3.10.12、PyTorch 2.14.0+cpu、
  Transformers 5.17.0、huggingface_hub 1.32.0；CUDA 不可用。
- 保持不变：模型 ID、revision、CPU 配置和五条输入。
- 在线检查：HTTP 200；本轮模型加载耗时：3.09s。
- 结果：四条有效文本的标签和分数与第一遍一致；
  整数输入仍触发并记录 ValueError；最终保存五条记录。
- 原始证据：
  [本轮输出](week02/evidence/review-20261007/predictions.jsonl)。
- 当前结论：现有环境中，Notebook 重启后顺序运行成功；
  反讽误判也再次出现，高分类分数不保证语境判断正确。
- 验证范围：尚未验证全新环境重建，也未开展总体准确率评测。
- 下一步：复盘固定 revision 与离线缓存的关系，
  整理模型选择、正常结果和失败案例的组会展示。

  #### 离线缓存验证

- 验证方式：设置 HF_HUB_OFFLINE=1，运行独立缓存检查脚本；
  模型、revision、CPU 设备和测试文本保持不变。
- 结果：模型成功加载，输出 POSITIVE，
  score 为 0.9996985197067261，与在线实验一致。
- 原始证据：
  [离线日志](week02/evidence/review-20261007/offline-cache-output.txt)。
- 结论：当前缓存包含这次固定版本推理所需的文件，
  独立脚本可以在 Hub 离线模式下完成推理。
- 限制：未验证其他版本或模型；完整 Notebook 含在线连接检查，
  本次结果不能证明整个 Notebook 可离线运行。

#### 归档与组会准备

- 主线复盘已通过
  [PR #9](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/9)
  合并，合并提交为 `2d0bfb8`。
- 模型对比表已补充 DistilBERT 参数规模、模型选择理由，
  并明确 Qwen 的本机运行情况尚未验证。
- 组会展示主线：
  模型选择 → 固定版本与 CPU 配置 → 正常输出 →
  反讽误判 → 离线缓存结果 → 当前限制。
- 当前已验证：现有环境重启内核后的顺序运行，
  以及固定版本模型的 Hub 离线缓存加载。
- 尚待验证：全新环境重建；更多样例或统一测试集上的效果。

## Week 03：AI 辅助编程与人工验证

### 本周目标

以 Week 1 的图片信息工具为对象，练习明确需求、获取 AI 建议、人工审查、测试验证和记录取舍。

### 已完成

- 编写 `week03/task-card.md`，明确只支持实际格式为 PNG 和 JPEG。
- 在 VS Code 中使用 GitHub Copilot 完成需求审查、测试建议和最小实现补丁建议，记录三轮关键交互。
- 保留 Week 1 原有三个测试，并扩充至九个测试。
- 人工补充“BMP 内容使用 `.png` 文件名”和“文本内容使用 `.png` 文件名”两个场景，检查程序是否错误依赖扩展名。
- 修改 `week01/src/image_info.py`，使用 Pillow 识别出的实际图片格式判断支持范围。
- 检查实现和测试 diff，完成代码审查、AI 使用记录与 Week 3 README。

### 实际验证结果

修改实现前，七项测试中有两项因 BMP 被错误接受而失败，结果为 `2 failed, 5 passed`。修改实现并补充边界测试后，九项测试全部通过，结果为 `9 passed in 0.23s`。

手动运行原有 PNG 样例，仍输出宽 `640`、高 `480` 和格式 `PNG`；`--help` 正常显示帮助信息。原始测试输出保存在 `week03/test-before-fix.txt` 和 `week03/test-after-fix.txt`。

### 本周收获与限制

AI 给出的代码和测试只是待验证的建议。测试不仅要覆盖正常输入，还应能发现错误实现；本周“真实 BMP 内容却使用 `.png` 文件名”的测试说明只检查扩展名并不可靠。

当前工具只处理单张本地 PNG 或 JPEG，不进行 OCR、完整像素解码或任意不可信图片的资源限制检查。


### Git 与 PR

Week 3 工作分支：`feat/week03-ai-validation`。[Week 3 PR #4](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/4) 已于 2026-09-28 合并到 `main`，合并提交为 `0b95ec6`。