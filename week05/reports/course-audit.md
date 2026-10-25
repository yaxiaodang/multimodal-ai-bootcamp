# Week 5 路线核对｜2026-10-25

核对依据：[12 周路线的 Week 5](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-5document-ai)、[Document AI 专题](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/07_Doc_AI/)、[学习记录模板](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/11_Learning_Log_Template/)。本页是 Codex 依据仓库和本人回答所做的证据核对，不是导师验收或对学习时长的推断。

## Week 5 主线与补齐项

| 要求 | 当前证据 | 结论 |
| --- | --- | --- |
| 数字 PDF、扫描件、复杂表格各一份，说明来源和权限 | [来源](../samples/README.md)、[输入清单](../configs/document-manifest.json) | 已完成；均为虚构自制单页，非真实扫描或正式 benchmark |
| 文档登记包含类型、语言、分辨率、任务单位、目标输出、风险与指标 | [document-inventory.csv](../document-inventory.csv) | 本次补齐独立 CSV；矢量 PDF 不伪称有固定原生 DPI，扫描图像核对为 150 ppi |
| 运行前人工预期与工具输出分开保存 | [人工预期](../docs/manual-expectations.md)、两轮 snapshots | 已完成有限核心参考，不宣称全页逐字或框标注 |
| 区分 OCR、layout、table、parsing、VQA，并有任务地图 | [任务地图入口](../task-map.md)、[完整表](../docs/task-map.md) | 已完成；公式与字段抽取概念补充说明，不当作已运行模型 |
| 运行公开工具并逐项对照 | [两轮评价](layout-comparison.md)、[原始预测索引](../predictions/README.md) | 本人实际运行，两轮各 11 项；新增索引而不移动或改写 raw TXT |
| 保存不少于三类文档问题及性质 | [错误分析入口](../error-analysis.md)、[案例](error-analysis.md) | 覆盖顺序、公式/标题/表格表示及 OCR 范围；不虚构三种独立 OCR 算法故障 |
| 一个自主探索方向及可验证问题 | [研究记录](../docs/research-direction.md) | 已选择 A，只追加 -layout；输入、版本和规则保持一致 |
| 选择适用指标并解释理由 | [指标选择](../docs/metric-choice.md) | 本人选物理可读性，理由是排版后更方便阅读；固定人工检查与可读性分开，不计算总体准确率 |
| 不只凭“看起来不错”评价 | D3 顺序、T2 字段、D4 上下标、T1 合并范围及原文定位 | 已完成；本人选择可读性不取消其余独立检查 |
| 例会准备含任务地图、最困难文档、Week 6 问题 | [展示稿](meeting-notes.md)、[交接](../docs/week06-handoff.md) | 已准备；本人授权 Codex 选复杂表格及结构化表格 Pipeline，实际演练尚未记录 |
| learning-log 的路径、时间、环境、AI 使用、限制和下一步 | [学习日志](../../learning-log.md) | 已按模板整理；本人明确时长未统计，自评维持已跑通/可解释，不假填 24 小时 |
| GitHub 成果可审阅 | [PR #13](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/13) | 已创建草稿，发布 fd73a3b 与回执匹配；补齐资料通过同一发布入口更新到该 PR；核对时仍未合并 main |

结论：原有主线实验并不缺一个必须重跑的模型实验；本次补齐的主要是专题提交入口、完整文档登记、指标理由、例会交接与状态一致性。按已完成任务范围归为标准路径内容，自报学习时长未统计；不把建议投入当成完成条件或实际投入。

## 不属于现在重做的任务

- Week 6：三份文档的 Docling Markdown/JSON Pipeline、日志和质量规则，目前为交接计划，未假称完成。
- Week 7：固定测试集、完整参考、可计算质量指标、切片结果和 benchmark，不以本周三页与类别计数替代。
- 专题跨周要求：至少一次模块化路线与端到端 VLM 的实际比较。当前未做，已列入 [跨周待办](../docs/route-comparison.md)；两次 pdftotext 设置对照不能代替它。
- 进阶代表性论文、完整评测或后训练不因页面链接存在就变成本周必须立即追加的实验。

## 工程收尾与学习边界

PR #13 已关联本任务。基础核对与入口准备由 Codex 完成；个人判断来源保持区分。实际例会演练与跨环境复现未发生，不伪造为已完成。PR 合并是单独的仓库操作，不是课程通关审批；当前草稿状态与 main 保持事实记录。

本核对记录随本次补齐提交保存。fd73a3b 是编写时已核验的远程提交，不宣称是以后每次发布的最新提交；实际发布以 `.git/week05-publish-receipt.json` 和 PR 页面为准。
