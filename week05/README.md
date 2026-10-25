# Week 05｜Document AI 任务地图

当前阶段：第五周三文档主线、两轮各 11 项评价、A 方向探索与本人复盘已完成。对照 [Document AI 专题](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/07_Doc_AI/) 补齐文档清单、指标理由、原始预测入口和例会交接，见 [路线核对](reports/course-audit.md)。本人学习时长未统计，自评维持已跑通/可解释，未验证全新环境复现；实际例会演练未记录。

Git 保存：最新已核验远程提交 fd73a3b；[PR #13](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/13) 已创建并关联，仍为草稿、未合并 main。本次专题对齐资料随本次补齐提交保存，发布入口会推送并更新该 PR，见 [同步记录](docs/github-sync.md)。

课程入口：[第五周要求](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-5document-ai)。
本周目标：理解任务边界并依三类文档选择研究问题。最困难文档按本人授权选复杂表格，Week 6 优先解决明确的网格/合并范围与字段对应，见 [交接](docs/week06-handoff.md)。

## 整体流程与分工

| 步骤 | 本人完成的学习活动 | Codex 完成的基础工作 | 留下的证据 |
| --- | --- | --- | --- |
| 1. 认识任务 | 用自己的话区分五种任务及公式识别 | 提供解释、讨论例子 | docs/task-map.md |
| 2. 选择文档 | 选择数字 PDF、扫描件、复杂表格文档各一份 | 归档、记录来源与版本、计算哈希 | samples/README.md、configs/document-manifest.json |
| 3. 写人工预期 | 看原页，标注标题、段落、表格、公式、阅读顺序 | 整理记录；在运行前保存版本 | docs/manual-expectations.md |
| 4. 运行和对照 | 运行命令，检查工具输出，解释与预期的差异 | 准备命令或脚本、配置、日志位置 | runs/、reports/comparison.md |
| 5. 分析与选题 | 归纳至少三类实际错误，选择一个探索方向 | 整理证据与学习记录 | reports/error-analysis.md、docs/research-direction.md、../learning-log.md |

人工预期须先于工具输出形成。本轮只评价本人已确认的核心事实；Codex 补充但本人未单独确认的区域与字段保持独立说明，不宣称全页完整标注。每次运行保存人工预期和检查项的快照与哈希。后续若发现标注错误，应记录修订理由并保留原版本；不能照着工具答案倒写预期。

## 目录与用途

| 位置 | 用途 |
| --- | --- |
| document-inventory.csv | 三文档的来源、语言、分辨率、任务单位、风险和适用判定 |
| task-map.md / error-analysis.md / predictions/ | 对齐专题目录的索引；完整正文与原始结果仍保留在 docs/reports/runs |
| docs/metric-choice.md / docs/week06-handoff.md | 本人指标理由、按授权选定的例会交接与未来成功标准 |
| reports/course-audit.md | 第五周完成情况与 Week 6–7 跨周待办 |
| samples/ | 三份自制 PDF、页面 PNG 预览、制作来源与字体许可 |
| configs/document-manifest.json | 输入路径、制作方法、版本、页码、文件与预览哈希、依赖与字体信息 |
| docs/task-map.md | 对话与实际结果整理的任务地图，指标边界另有说明 |
| docs/manual-expectations.md | 人工预期结构，独立于工具输出 |
| docs/research-direction.md | 本人选择 A；Codex 整理的运行前问题、假设和判断规则 |
| configs/layout.json / reports/layout-comparison.md | 只追加 -layout 的配置与已完成的 11 项评价、P1/P2 对照 |
| runs/ | 首次基线已归档；后续运行各自保留原始文本、日志、配置与参考快照 |
| reports/ | 阶段报告、逐项评价、类别计数与有原始证据的问题分析 |
| reports/report.md / metrics.json | 首次基线阶段报告与人工类别计数，不是总体准确率 |
| reports/layout-comparison.md / layout-metrics.json | 布局对照的 11 项评价、补充观察及假设对照，不是总体准确率 |
| docs/annotation-history.md | 从学习日志归档的分步作答与历史状态，当前状态以阶段报告为准 |
| evidence/environment.txt | 本次实际检查到的环境信息 |
| evidence/material-preparation.txt | 输入制作检查与同环境重复生成的原始记录，非工具实验输出 |
| scripts/prepare_documents.py | 生成三份教学文档与预览，不运行 OCR / 文本提取，不填写人工预期 |
| scripts/run_baseline.py | 核对输入后调用 pdftotext，保存原始输出与证据，不自动评分 |
| configs/baseline.json | 固定工具版本、页码、编码、超时与参考文件路径 |
| configs/evaluation-plan.json | 根据已确认核心事实整理的 11 项人工检查；未确认的补充不纳入 |
| requirements.txt | 材料生成依赖，与根目录基础依赖分开保存 |

## 环境与建议的初始工具

已检查 Ubuntu 22.04.5 LTS；项目 `.venv` 为 Python 3.10.12；PDF 工具为 Poppler 22.02.0。系统默认 `python3` 为 3.14.7，与项目解释器不同。材料制作阶段新增安装 ReportLab 4.4.10，沿用 Pillow 11.3.0 与 charset-normalizer 3.5.1；依赖检查通过，未安装 OCR / Docling，未下载模型。

中文和数字分别使用已有的 DroidSansFallbackFull.ttf 与 DejaVuSans.ttf。生成程序嵌入字体子集，扫描 PDF 则只保存整页图像。系统准备依赖是 poppler-utils、fonts-droid-fallback、fonts-dejavu-core，本机均已具备。

本轮使用 `pdftotext` 建立 CPU 文本提取基线，再用实际缺失的结构提出问题。它读取 PDF 已有文字内容，不执行扫描图像 OCR；纯文本也不显式表示标题层级、单元格合并等结构。扫描 PDF 可能已有 OCR 文字层，不能仅凭文件扩展名或能否选中文字判定来源。当前这份自制扫描 PDF 未添加文字层，实际结果只有换页符，没有正文。

参考：[Ubuntu pdftotext 手册](https://manpages.ubuntu.com/manpages/jammy/man1/pdftotext.1.html)。课程列出的进一步工具入口：[PaddleOCR](https://www.paddleocr.ai/main/en/index.html)、[Hugging Face 文档问答](https://huggingface.co/docs/transformers/tasks/document_question_answering)。

## 当前唯一开始入口

概念辨析记录见 [任务地图](docs/task-map.md)，运行前事实见 [人工预期](docs/manual-expectations.md)，检查范围见 [evaluation-plan.json](configs/evaluation-plan.json)。从三类维度分别观察：文字是否出现、阅读顺序是否符合原页、结构关系是否得到表达。不把程序结束当成任务正确，也不把纯文本中出现数字当成表格关系完整。

本人已选择 A，运行前问题与规则见 [方向记录](docs/research-direction.md)。本轮流程：同样的三份输入 → 只追加 `-layout` → 新建目录保存结果 → 先看物理排版，再按原 11 项检查逻辑顺序与结构。配置包含运行前假设，随本轮配置快照保存；提取程序不需要改动。

本人已执行以下命令，完成 [布局对照运行](runs/baseline-20261025T113919-b11603/)，无需重复运行。两轮的实际提取与 11 项评价均已完成，本人已给出独立总结，当前在已登录的 VS Code 终端运行下方发布入口，推送专题对齐补充并更新已有 PR #13。无需重跑提取；例会材料与下一周交接已准备。命令保留供复现：

```bash
.venv/bin/python week05/scripts/run_baseline.py --config week05/configs/layout.json
```

作用：使用项目 Python 和布局对照配置，仍由同一程序调用 pdftotext，只多传 `-layout`，尝试保留页面物理排版。输出到新的 `runs/baseline-时间-标识/`，不覆盖首次基线；元数据中的 `config.name` 为 `pdftotext-layout-v1`。它不新增 OCR 或自动评分。三份均正常结束，状态与哈希已核对，接下来逐项观察内容。

Codex 已完成只核对版本与输入的准备检查，见 [准备证据](evidence/layout-preparation.txt)。对照记录表见 [layout-comparison.md](reports/layout-comparison.md)。查看布局时用等宽字体并关闭自动换行；物理对齐与逐行文本顺序分开判断。

以下为已完成的首次基线操作说明，供复现查阅，当前无需重复运行。

本人本次直接执行 `.venv/bin/python week05/scripts/run_baseline.py`，作用是明确使用项目解释器调用基线入口；即使提示符不显示 `(.venv)` 也不影响该命令。下方激活环境的方式同样可用，不需要为提示符再跑一遍实验。

如需在 VS Code 中切换到本仓库，在 **Remote SSH 连接 Ubuntu 后的终端**运行：

```bash
cd /home/yaxiaodang/multimodal-ai-bootcamp
```

作用：把终端工作目录切换到仓库根目录，后续相对路径都从这里开始。文件可通过 VS Code 左侧资源管理器打开。Python 程序出现时，再使用下列命令：

```bash
source .venv/bin/activate
```

作用：让当前终端的 `python` 和 `pip` 使用已有项目虚拟环境。它不安装依赖，也不影响系统 PDF 命令。

由本人在上述目录运行：

```bash
python week05/scripts/run_baseline.py
```

作用：按 configs/baseline.json 调用系统 pdftotext，依次处理三份 PDF，创建新的 runs/baseline-日期时间-标识/ 目录。目录时间按 Asia/Shanghai 记录；完整命令、版本、输入哈希、代码版本、每份输入的耗时与退出码、原始文本、参考快照和空白 review.csv 自动保存。无需 GPU、联网或模型下载。

实际提取参数为 `-f 1 -l 1 -enc UTF-8`，分别指定起始页、结束页和输出编码。本轮不传 -layout，使用工具默认阅读顺序策略；未来若做对照，可仅改变布局选项。本轮不是两个模型或两种方法的对照实验。

程序只保存结果，不改写原始 txt，不自动填评价。即使输出只有空白且工具退出码为 0，也会按实保存；需要本人判断这是工具范围、内容缺失还是其他问题。某份提取失败时保留日志并继续其他输入，最后返回非零状态。

准备核对入口（Codex 已执行）：

```bash
python week05/scripts/run_baseline.py --prepare-only
```

作用：检查版本、输入哈希、人工预期和检查项文件是否可用，不提取正文，也不创建实际运行目录。新增源码语法、帮助、正常准备及错误哈希拒绝检查已通过，见 [准备记录](evidence/baseline-preparation.txt)；以上是运行前准备证据；首次实际提取及评价现已完成。

运行后先打开新目录的 digital_pdf.txt，对照原页检查左右两栏的段落顺序，再检查 scanned_pdf.txt 与 complex_table.txt。每一项填写原始文件定位、本人判定及理由，可先在对话中表达，由 Codex 归档。

## 发布收尾入口

```bash
.venv/bin/python week05/scripts/publish_github.py
```

作用：在已登录 GitHub 的 VS Code 内置终端推送已提交的第五周分支、核对远程提交并创建或更新指向 main 的同一个草稿 PR。它不运行学习实验、不提交工作区文件，也不自动合并。PR 正文见 [草案](reports/pull-request.md)，例会材料见 [展示草案](reports/meeting-notes.md)；认证和失败处理见 [同步说明](docs/github-sync.md)。

## 材料生成程序的作用与复现

程序依次绘制数字页、制作模拟扫描页、绘制复杂表格页，渲染最终 PDF 预览并写入输入清单。它只准备输入，不提取正文，不生成参考标注或评价。制作检查见 [记录](evidence/material-preparation.txt)，教学内容与许可见 [来源说明](samples/README.md)。

以下是制作复现说明，本轮已由 Codex 完成，不是当前需要本人执行的学习任务。所有命令从仓库根目录执行，并使用已激活的 `.venv`。

```bash
python -m pip install -r week05/requirements.txt
```

作用：安装固定的材料生成依赖。本机已完成；新机器还需准备上述系统工具和字体。

```bash
python week05/scripts/prepare_documents.py --help
```

作用：查看材料生成程序的用途和输出目录参数，不修改任何材料。

```bash
python week05/scripts/prepare_documents.py --output-dir /tmp/week05-materials-rebuild
```

作用：在指定目录重新生成 PDF、预览与清单；目录已有生成材料时会拒绝覆盖。该操作不修改本仓库中的人工预期。默认不传参数时输出到 week05，但已有输入受到覆盖保护。

固定页面内容与坐标，无随机采样，PDF 内部元数据使用 invariant 设置，因此 pdfinfo 中的内部创建时间固定为 2000 年；实际材料制作日期以清单 created_on（2026-10-24）与制作记录为准。本次只验证相同环境的重复生成，其他库或字体版本可能产生不同字节，应依据清单固定版本。

生成库参考：[ReportLab 4.4.10](https://pypi.org/project/reportlab/4.4.10/)、[ReportLab 字体文档](https://docs.reportlab.com/reportlab/userguide/ch3_fonts/)。

## 完成标准

- [x] 三份文档的来源、许可、页码、版本、文件哈希已登记；本人核心事实观察已完成。
- [x] 在运行前写出有限核心人工预期，未确认的补充范围单独注明；不存在的表格/公式明确写“无”。
- [x] 任务地图已结合实际结果整理，区分文字提取、OCR、结构解析与问答；本人已解释扫描件的工具范围问题。
- [x] 本人执行工具，保留未修改的输出、配置、终端日志和退出状态。
- [x] 11 项已对照，记录多类有原始证据的问题，分清顺序错误、表示局限与不支持，不把同因检查虚增为独立模型故障。
- [x] 本人选择 A：版面/表格；Codex 整理运行前研究问题与假设。
- [x] 本人运行布局对照并完成逐项观察，Codex 依据原规则整理 11 项评价与证据。
- [x] 本人独立说明布局改善及阅读顺序/公式的限制，Codex 补充证据范围。
- [x] 本人授权 Codex 选复杂表格及 Week 6 首要 Pipeline 问题；本人确认维持当前自评，例会材料已准备。
- [x] 按专题补齐 document-inventory.csv、指标理由、原始 prediction 索引与提交入口。
- [ ] 实际例会演练未记录；跨环境复现未验证，均不伪造为完成。
- [x] 更新根目录 learning-log.md，记录当前基线的 AI 使用与人工核验来源；本人确认时长未统计，自评维持已跑通/可解释。
- [x] 首次阶段成果已同步 GitHub，远程核验提交 51dd75c。
- [x] 收尾文档已推送，远程核验提交 a87d468。
- [x] 发布修复已推送，远程核验 fd73a3b，[草稿 PR #13](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/13) 已创建并关联。
- [x] 专题补充与 PR 更新入口已准备；发布时核验最新提交并更新同一 PR，实际合并另行处理。

若当前材料未观察到三类错误，先如实记录，再增加有针对性的合法样本或页码；不得把预想风险写成已经发生的错误。三份教学文档不构成通用 Benchmark。
