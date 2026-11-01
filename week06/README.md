# Week 06｜Docling 文档解析 Pipeline

状态（2026-11-01）：流程、固定输入清单、运行前质量检查草案和学习记录已准备；尚未安装 Docling、下载模型、实现或运行解析入口，尚无本周解析结果。独立虚拟环境由 Codex 准备；完整依赖将在进入环境准备步骤时由 Codex 安装、固定版本并核验。

课程依据：[第六周主线](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-6docling-pipeline)、[学习记录模板](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/11_Learning_Log_Template/)。实现前核对 [Docling 安装说明](https://docling-project.github.io/docling/getting_started/installation/) 与 [Quickstart](https://docling-project.github.io/docling/getting_started/quickstart/)，以实际安装版本为准。

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
- [质量规则草案](docs/quality-plan.md)：运行前列出检查目标，结果保持待核验。
- [人工核对表](reports/quality-review.csv)：待本人实际检查后填写；不是预测结果。
- [运行目录约定](runs/README.md)：计划保存的原始产物及失败记录。
- [环境准备证据](evidence/preparation.json)：本次实际检查情况。
- [连续学习记录](../learning-log.md)：在 Week 06 节追加实际进展。

## 当前第一步

先理解上面的数据流，对照第五周的 [复杂表格原页](../week05/samples/previews/complex_table.png) 和 [交接目标](../week05/docs/week06-handoff.md)，思考：哪些信息适合在 Markdown 中读，哪些关系需要检查 JSON 的单元格表示？在对话中用自己的话描述即可，由 Codex 归档，不要求研究具体函数。

后续进入运行步骤时，由 Codex 提供一条已核验的实验入口及每个参数的作用。当前没有可运行的 Docling 实验命令。

环境安装属于 Codex 执行的基础工作；解析、选择实验变量、判断结果与解释发现属于本人的学习活动。每完成一步再继续下一步，不预先标记学习或实验完成。
