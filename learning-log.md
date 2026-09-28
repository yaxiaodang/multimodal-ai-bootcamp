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

## Week 02：Hugging Face 与 CPU 推理

### 本周目标

学习如何查看模型与数据集信息，固定模型版本，在 CPU 上完成一次推理，并保存可检查的结果与失败案例。

### 已完成

- 学习 Hugging Face 的模型、Model Card、模型版本和 Pipeline 等基础概念。
- 创建 `week02/transformers-demo.ipynb`，选择项目 `.venv` 内核运行。
- 使用模型 `distilbert/distilbert-base-uncased-finetuned-sst-2-english`。
- 将模型版本固定为 `714eb0fa89d2f80546fda750413ed43d93601a13`，并指定 CPU 运行。
- 运行 3 条正常文本、1 条反讽文本和 1 条无效输入，将 5 条记录保存到 `week02/predictions.jsonl`。
- 编写 `week02/run-metadata.yaml` 和 `week02/failure-case.md`。

### 运行环境与观察

本次 Notebook 输出的环境为 Python 3.10.12、PyTorch 2.14.0+cpu、Transformers 5.17.0、huggingface_hub 1.32.0；CUDA 不可用。

正常样例分别得到正面、负面和负面分类。反讽句 “Great, another two-hour delay. Just what I needed.” 得到 `POSITIVE`，分数约为 `0.993`；按语境阅读，这句话表达的是负面态度。整数 `12345` 不是有效文本输入，程序记录了 `ValueError`。

这些是少量样例的观察结果，不能当作模型整体准确率。

### 遇到的问题与解决

Ubuntu 虚拟机起初无法访问 Hugging Face，模型加载时反复请求 `config.json` 并报网络不可达。Windows 能访问网站，但虚拟机和 Jupyter 内核需要分别检查网络设置。配置可用的网络代理后，Notebook 成功访问模型文件并完成 CPU 推理。

使用 Notebook 时还需要区分 Markdown 单元和代码单元：说明文字放在 Markdown 单元，Python 语句放在代码单元；运行代码前确认选择了正确的 `.venv` 内核。

### 我目前的理解

- 模型 ID 用来指定模型；固定的 revision 用来指明本次使用的具体版本。
- Pipeline 把模型加载和推理步骤组合起来，但仍需要核对任务、输入和输出。
- 分类分数反映模型对其输出标签的分数；反讽案例说明高分结果仍可能与人的语境判断不一致。
- 无效输入造成的程序错误，与模型对有效输入判断错误，是两类不同的问题。
- 没有独立显卡也可以完成本周的 CPU 推理；首次下载模型仍依赖网络。

### 待完成

- [ ] 核对并完成 `model-comparison.md`。
- [ ] 完成所选数据集的调查记录，核对实际文件名及引用信息。
- [ ] 完成一项进一步探索，并保存实际操作与结果。
- [ ] 重启 Notebook 内核，从头运行全部单元，核对输出文件。
- [ ] 检查 `week02/README.md`、运行信息和依赖记录是否与实际一致。
- [ ] 提交 Week 2 分支，并在合并后记录完成情况。

完成一项再勾选一项；如果实验结果与预期不同，把实际结果写在这里。

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