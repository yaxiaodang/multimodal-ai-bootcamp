# Week 5 任务地图入口

本页对齐 Document AI 专题的提交目录，完整的“任务—输入—方法—输出—指标/人工规则—常见错误”表仍位于 [docs/task-map.md](docs/task-map.md)，避免重复维护两份正文。

- [三类文档清单](document-inventory.csv)：来源、许可/隐私、页面类型、语言、分辨率、目标任务、任务单位、预期输出、风险区域与适用判定。
- [指标选择与理由](docs/metric-choice.md)：明确当前评价单位，以及未计算 CER、TEDS 的原因。
- [原始预测索引](predictions/README.md)：两轮、每轮三份原始文本及对应元数据/评价表。
- [问题分析入口](error-analysis.md)：区分实际顺序错误、结构表示局限与工具不覆盖的能力。

本轮是 PDF 文字提取及结构保留观察，唯一实验变量为 -layout；不是 OCR、完整解析或 VQA 模型能力评测。任务地图由 Codex 整理，本人理解与实际观察的来源在正文中披露。
