# Week 06｜Docling 文档解析 Pipeline

状态（2026-11-05）：三文档主线、10项人工核验及本人选择的Markdown/JSON表示探索已完成。检查计数为正确6、部分正确2、错误1、结构未表达1，不计算总体准确率。证据与限制见 [实验报告](reports/report.md)；核心知识见 [复习材料](docs/core-knowledge.md)。本人自评、实际学习时长及实际例会演练未记录。

课程依据：[第六周主线](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-6docling-pipeline)、[学习记录模板](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/11_Learning_Log_Template/)。实现前核对 [Docling 安装说明](https://docling-project.github.io/docling/getting_started/installation/) 与 [Quickstart](https://docling-project.github.io/docling/getting_started/quickstart/)，以实际安装版本为准。

例会展示入口：[精简 Notebook](reports/meeting-demo.ipynb)，配套 [约4分钟讲稿](reports/meeting-notes.md)。参考第四周样式，嵌入复杂表格和数字PDF原页，五个只读代码单元的真实输出已保存。直接打开即可查看；如需重跑展示代码，选择项目 `.venv` 内核并保留完整仓库，不需加载Docling或重新解析PDF。文档与图片嵌入检查见 [验证记录](evidence/meeting-notebook-check.json)。实际本人演练尚未记录。

## 主线任务

沿用第五周的数字 PDF、扫描件、复杂表格各一份，用 Docling 导出未经修改的 Markdown 和 JSON，建立有输入校验、配置、日志、耗时与失败退出码的命令行 Pipeline，再由本人核对结构是否正确。

延续 [第五周交接](../week05/docs/week06-handoff.md)：复杂表格是优先研究点，三类文档都必须解析。重点检查 7×6 逻辑网格、合并范围，以及“纸张—第二季度—数量 12 / 金额 60”的对应关系。只找到数字不足以说明结构正确。

## 整体流程与分工

| 阶段 | 本人亲自完成 | Codex 直接完成 | 证据 |
| --- | --- | --- | --- |
| 1. 理解任务 | 说明输入、解析、输出与质量核对之间的关系 | 整理流程与已有交接 | 本 README、学习记录 |
| 2. 准备环境与固定输入 | 阅读三份原页，回顾原有人工预期 | 创建独立环境、安装并锁定依赖、核对输入哈希；明确中文 OCR 配置与模型来源 | configs/input-manifest.json、evidence/ |
| 3. 建立入口与首轮解析 | 在 VS Code 的 Ubuntu 远程终端亲自执行实验命令 | 准备解析脚本、配置、帮助、日志与错误处理，逐条解释命令 | scripts/、configs/、runs/ |
| 4. 检查与解释 | 对照原页与原始 Markdown/JSON，给出逐项判断及依据 | 辅助定位结构字段，整理本人观察，记录机械检查结果 | reports/quality-review.csv、每轮日志与检查结果 |
| 5. 分析与一次探索 | 解释三类文档差异，选择一个探索方向并亲自操作 | 按选择准备比较方案和程序，保持原始证据 | reports/、独立运行目录 |
| 6. 复盘与 GitHub 保存 | 给出发现、限制与下一步，准备一条命令和成功/失败案例 | 按事实更新 learning-log.md，提交并同步本周材料 | 学习记录、提交/PR 与同步记录 |

默认建议标准路径，分步推进；路径选择、实际学习时间与自主评价以本人后续表述为准。

## 实现逻辑

```text
三份固定 PDF + 输入来源/哈希 + 配置
    ↓ 输入校验
Docling 解析：利用 PDF 文字或 OCR 获取文字，识别版面与表格，组织文档结构
    ↓
结构化文档对象
    ├─ Markdown：便于阅读标题、段落和表格
    └─ JSON：检查元素、单元格及其结构关系
    ↓
机械检查 + 本人对照原页进行内容/结构核验
    ↓
保留原始输出、日志、耗时、失败记录与人工判断 → 分析 → 复盘
```

这是理解数据流的简图，实际组件与字段由安装版本和配置决定。常规 Markdown 表格对跨行、跨列合并的表达有限；JSON 提供检查结构的机会，但是否恢复正确仍需证据。标题文字、元素角色、标题层级分别核对，不能假定默认配置一定恢复层级。

与第五周的区别：当时 pdftotext 主要读取 PDF 已有文字，未执行扫描 OCR；本周研究可供程序继续利用的结构。模型下载失败、程序执行失败与内容解析错误分别记录。三份教学样例的检查不能替代正式 Benchmark。

## 文件入口

- [输入清单](configs/input-manifest.json)：复用 `week05/samples/` 的原始文件，不重制、不复制出另一份输入。
- [运行前质量规则](docs/quality-plan.md)：保留原始检查目标；实际判定见核对表。
- [人工核对表](reports/quality-review.csv)：10项已由本人反馈并由Codex整理，判定包含错误与限制；不是模型预测。
- [运行目录约定](runs/README.md)：计划保存的原始产物及失败记录。
- [环境准备证据](evidence/preparation.json)：本次实际检查情况。
- [环境与命令说明](docs/environment.md)：所有安装、检查和实验命令的作用；本机环境见 [environment.json](evidence/environment.json)，模型来源及哈希见 [model-preparation.json](evidence/model-preparation.json)。
- [解析配置](configs/baseline.json)、[锁定依赖](requirements-lock.txt)、[解析入口](scripts/run_pipeline.py)：CPU、2 个线程，开启中文 OCR 和准确表格解析，公式增强关闭。
- [连续学习记录](../learning-log.md)：在 Week 06 节追加实际进展。

## 当前状态与复习入口

本人已完成分步和六项集中核验，不需要重复运行。首轮耗时：数字页18.987秒、扫描件92.008秒、复杂表格26.4093秒，均包含模型加载，不作为纯推理速度或学习时长。

- [报告](reports/report.md)：三文档差异、10项判断、失败案例及Markdown/JSON表示比较。
- [核心知识](docs/core-knowledge.md)：数据流、任务边界、表格关系、导出范围、质量与复现证据。
- [例会 Notebook](reports/meeting-demo.ipynb) 与 [配套讲稿](reports/meeting-notes.md)：一条命令、成功与失败案例、表示差异及下一步；图片嵌入、代码输出已保存，实际本人演练尚未记录。
- [分步回答](docs/learning-notes.md) 与 [阶段日志归档](docs/annotation-history.md)：保留提示、更正及过程，不改写为全部独立答对。

本人明确选择表示方向并总结Markdown便于人读、JSON明确结构；本轮复用已有两种导出，不新增推理、不声称预注册消融，未比较DocTags或测试下游任务。

工作区复杂表格Markdown末尾的附加文字继续保留，未提交为原始结果，原始归档不改写，见 [变化说明](reports/markdown-edit-note.md)。

以下命令保留供复现；本轮已运行：

在 VS Code 的 Ubuntu 远程终端、仓库根目录执行：

```bash
.venv-week06/bin/python week06/scripts/run_pipeline.py
```

作用：明确使用第六周环境，依默认配置顺序处理三份固定 PDF。每次新建 `runs/baseline-时间-标识/`，按文档 ID 保存原始 `document.md`、`document.json`、日志、转换状态与机械检查；整轮保存命令、版本、配置/源码/参考快照、耗时、退出码与待本人核验的 `review.csv`。模型已下载；不需激活环境或重复安装。

一份处理失败会记录原因并继续其他输入，整轮返回非零退出码。即使三份均 completed，也只说明转换和文件/格式检查通过，结构正确性仍由本人判断。程序耗时包含各文档模型加载，不等于纯推理时间或学习时长。

本人已提交终端输出并完成核验，历史 [集中核验包](reports/batch-review.md) 保留供复习；与 [第五周交接目标](../week05/docs/week06-handoff.md) 的对应及未解决限制见实验报告。

准备命令 `--prepare-only` 已由 Codex 执行，校验三份输入、依赖和选项，不下载模型或解析 PDF。五项工程检查使用临时目录和故障注入；它们不是学习实验。详见 [检查日志](evidence/engineering-checks.log) 和 [离线加载记录](evidence/model-loading-check.log)。最初的 preparation.json 保留首次准备状态，当前状态以 environment.json 和本 README 为准。

环境安装属于 Codex 执行的基础工作；解析、选择实验变量、判断结果与解释发现属于本人的学习活动。每完成一步再继续下一步，不预先标记学习或实验完成。
