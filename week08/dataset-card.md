# Week08 Dataset Card — fictional invoice text v1.0

本周是文本字段抽取的LoRA教学任务。输入是已转成文字的英语账单片段，输出为两个字符串字段total和currency；不接受PDF/图像。可理解为Docling/OCR之后的一个下游环节，但没有接入真实解析器。

来源为本仓库 [prepare_data.py](scripts/prepare_data.py) 生成的120份全新虚构文本，seed=20261111。人工姓名、地址、账户、真实票据和第三方数据均未使用。制作者将这些合成数据按CC0-1.0提供，许可见 [CC0官方说明](https://creativecommons.org/publicdomain/zero/1.0/)。代码未据此改变整个仓库的许可。

| split | 数量 | 用途 |
| --- | ---: | --- |
| train | 96 | 唯一参与梯度更新的数据 |
| validation | 12 | 训练前后对比与每20步NLL观察；固定最终60步，不选最好checkpoint |
| reserved-test | 12 | 本周不推理、不调参；后续独立评价预留 |

生成前固定三个模板，按split独立ID区间分配，金额通过固定seed生成，每个split的币种USD/EUR/GBP及模板均衡。ID与完整文本跨split不重合；共享模板、输出结构、词汇意味着结果只反映有限同分布泛化，不能认作跨版面或真实领域泛化。金额虽可由subtotal+tax计算，本任务定义为复制total字段，不评价数值推理。

运行后的数据审计还发现：模板0/1/2分别恒对应USD/EUR/GBP，模板与币种完全相关；币种正确可能来自模板记忆，不能单独证明读取币种的能力。train与validation的total值没有精确重合，但这不能消除共享模板偏差。保留已冻结v1，如需检验此问题，应另建模板与币种独立组合的v2开发集，不能为改善结果修改本轮数据。见 [数据审计](evidence/data-audit.json)。

[freeze.json](data/freeze.json) 固定数据文件和生成器SHA-256；[训练计划](post-training-plan.md) 在训练前固定Prompt、评价和预算。生成器拒绝覆盖冻结v1；train.py先校验哈希再运行，reserved-test只用于完整性与划分数量检查、不用于模型输入或参数选择。

第7周冻结测试集用于文档解析，任务和指标不同。本实验完全不导入Week07 PDF、参考答案或预测；也不拿第7周baseline与本周JSON匹配率直接比较。后续若把adapter接入文档pipeline，需要先在开发数据上定义接口和新的下游参考，再单独制定联合评测协议。

限制：样本小，只有三种格式、三种币种、简单数字和英文；无OCR噪声、多语言、表格、缺失字段、恶意文本或多个total；不能用于真实财务处理，模型输出必须再核对原文。模型可能生成格式正确但数值错误的结果。
