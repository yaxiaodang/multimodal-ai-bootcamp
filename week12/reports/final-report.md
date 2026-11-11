# Capstone最终实验报告

结论：**对当前混合PDF，继续保留OCR；内容识别较好仍不足以支持表格结构可用。** 英文文本adapter仅作为教学候选，现有证据不能支持生产采用、A/B胜负或真实PDF字段抽取能力。

## 核心实验与统一评测

[设计卡](../capstone-design.md)固定展示问题，[协议](../../week10/configs/protocol.json)记录历史实验边界。相同Week07冻结24页，baseline配置与关闭OCR配置的算法差异仅为do_ocr。baseline复用历史原始运行，关闭OCR为Week10真实运行；本周只认证并重算，不将旧结果包装成新推理。

| 方法 | 内容相似度 | 阅读顺序 | 表格严格匹配 | 扫描内容相似度 | 历史总秒数 |
| --- | --- | --- | --- | --- | --- |
| OCR开启 | 0.967559 | 0.708333 | 0% | 0.950549 | 996.4 |
| OCR关闭 | 0.650709 | 0.500000 | 0% | 0.000000 | 352.1 |

数字PDF内容相似度两者均1.0，表格文档内容相似度均0.952128。扫描切片的退化解释了总体差异；默认去掉OCR会损害这类输入。这里的“改善”是相对关闭OCR保留扫描信息，没有声称开发了超过Docling默认的新算法。[自动重算表](results.md)与[结构化结果](results.json)可由开始命令重新验证。

内容分数对规范化文字做编辑距离比较；顺序指标比较预定标记的相对位置；表格strict核对网格、单元格文本及合并跨度。归一化文本接近并不保证结构正确。历史PDF时间包含每页加载，负载不同、无受控重复；PDF峰值内存未测，不能据此声称OCR关闭有严格2.8倍加速。

## 旁支实验：英文文本LoRA

同一reserved-test、Prompt、CPU FP32双线程、seed42、greedy最多32新token：base严格JSON正确0/12，Week09 A/B均12/12。A/B历史训练只差学习率0.001/0.0005；不是PDF模型，不能在中文PDF指标中排名。推理/加载评测总时间分别32.82/39.04秒、18.42/24.41秒、15.78/23.51秒，峰值RSS约1152MiB。无重复测时，不宣布速度胜者。

Week11的LoRA r4/r8机制验证使用12 validation：两者训练后均12/12，可训练参数230400/460800，占约0.171%/0.341%，训练203.53/209.70秒，峰值RSS1515.8/1459.4MiB。基座前后哈希不变、adapter重加载一致、12条合并greedy一致，logits满足既定绝对/相对容差。rank降低不保证总内存更小；alpha固定时alpha/r也改变，不能解释为纯容量效应。详见[复现报告](../../week11/reports/reproduction-report.md)。

## 证据索引与失败

| 主张/案例 | 输入与参考 | 配置与原始证据 |
| --- | --- | --- |
| 保留OCR可避免扫描页空输出 | [扫描PDF](../../week07/data/test/test_scan_01.pdf)、[参考](../../week07/references/test_scan_01.json) | [OCR开启配置](../../week10/configs/pdf-baseline.json)、[关闭配置](../../week10/configs/pdf-no-ocr.json)、[开启原JSON](../../week07/runs/baseline-20261111T144702-4ebb49/test_scan_01/document.json)、[关闭原JSON](../../week10/runs/pdf/baseline-20261111T160020-0f4498/test_scan_01/document.json) |
| 内容相近仍有表格结构失败 | [表格PDF](../../week07/data/test/test_table_01.pdf)、[参考](../../week07/references/test_table_01.json) | [原始JSON](../../week07/runs/baseline-20261111T144702-4ebb49/test_table_01/document.json)、[错误候选](../../week10/reports/error-taxonomy.md) |
| 英文adapter仅有小合成任务证据 | [数据卡](../../week08/dataset-card.md)、[reserved-test](../../week08/data/reserved-test.jsonl) | [原始suite及各预测](../../week10/runs/suite-20261111T080142898866Z/suite.json)、[统一结果](../../week10/reports/comparison.json) |
| 低秩机制可检查而非只看准确率 | [LoRA Paper Card](../../week11/paper-card.md)、[rank配置](../../week11/configs/rank-4.json) | [机制/训练suite](../../week11/runs/suite-20261111T081647230916Z/suite.json)、[归档核验](../../week11/evidence/verification.json) |

共保留42个方法×文档错误候选，涉及28个唯一文档（PDF16个）；[taxonomy](../../week10/reports/error-taxonomy.json)记录症状与原始输入，[人工CSV](../../week10/reports/manual-review.csv)仍待本人抽样复核。OCR关闭时转换进程可退出0，但空Markdown不满足pipeline机械检查，保留failed并按原协议计0。没有因失败删页或改预测。表格strict失败原因需结合原页与单元格复核，不能从分数独断根因。

## 成本、判断与限制

历史实验均本地CPU，GPU小时0、新增付费云费用0；电力、购置、能耗和维护工时未测，不把总成本写成0。本周归档重算耗时、Python及系统见[execution](../evidence/execution.json)，不将其当训练成本或本人学习时间。W&B训练项目为multimodal-ai-bootcamp-week09，A/B离线ID为3xryklnu/0h6gfu6a；[归档](../../week09/evidence/verification.json)保留失败运行与artifact核验。云端artifact版本及Report链接仍待本人登录同步。

事实：当前固定输入和原始输出支持以上数值；本周入口可重新评分。解释：扫描页依赖OCR，结构评价应独立于文字分。推测：更强模型或新数据可修复真实文档问题，目前尚未验证。合成模板共享、参考人工检查待完成、单seed、测试已消费、无独立新分布评测均限制结论。课程Week10“Week09模型在Week07 test上评测”未字面完成，原因是任务不兼容；Capstone明确保留此差距。

下一步先完成本人及同学核验，再按[四周计划](next-four-weeks.md)建立打破模板/币种关联的新dev和锁定final-test。最终答辩、个人自主阶段与个人判断不能由AI代填。
