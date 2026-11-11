# Project Card｜CPU文档解析与可审计评测

**状态：教学研究作品；AI已执行实验与归档核验，本人复核/同学复现/口头展示待完成。**

目的：让陌生读者从输入、配置、原始输出和指标判断一个方法能支持什么结论。主要任务是中文PDF→Docling Markdown/JSON；英文文本→账单字段JSON是独立的LoRA适配教学旁支，当前没有二者串联的端到端结果。

## 方法、版本与证据

- PDF数据：自制虚构CC0-1.0，24页test，三类各8页；[数据卡](../week07/dataset-card.md)、[冻结清单](../week07/data/freeze.json)。参考由生成规格提供，本人逐项复核尚待完成；不含真实账单或私人文件。
- PDF实现：Docling2.145.0、RapidOCR3.10.0、ONNX Runtime1.23.2，CPU两线程；[环境锁](../week06/requirements-lock.txt)、[固定模型与组件来源](../week06/evidence/model-preparation.json)。模型缓存不入库；各组件许可单独继承，不将整仓库统一宣称为CC0。
- 文本数据：虚构英文账单v1，96 train / 12 validation / 12 reserved-test；[数据卡](../week08/dataset-card.md)。test已在Week10消费，validation也多次使用，共享模板且模板/币种相关；没有真实分布独立泛化证据。
- 文本模型：`HuggingFaceTB/SmolLM2-135M@93efa2f097d58c2a74874c7e644dbc9b0cee75a2`，Apache-2.0；PEFT0.19.0，seed42；[训练环境与来源](../week11/evidence/environment-and-sources.json)。只存小adapter，基础模型另行按固定revision下载。
- 代码与证据版本：整合起点Git `5847fd1194406cd766730c48a1853b8eed0e857f`；本周交付版本见分支Git历史；[本周manifest](evidence/manifest.json)固定静态交付与上游证据，动态回执及本人填写文件另列，不形成循环SHA依赖。
- 结果：见[从原始结果重算表](reports/results.md)与[最终报告](reports/final-report.md)。每项主张都链接输入、配置、原始输出；两项任务不合并排名。

## 用途与不适用场景

适合：CPU学习实验、离线评分复现、展示OCR消融、学习LoRA机制和证据组织。新输入可按Week06接口处理，但许可/隐私需先自行核实。

不适合：自动审批/支付/记账、临床或法律判断、未经核对的生产知识库写入、真实发票质量承诺、把同模板12条全对当成通用能力、把文字相似度当成表格结构正确。

## 限制与伦理风险

扫描页仍有OCR顺序/内容错误，表格strict为0，进入RAG或字段抽取前需人工核查和结构修正。归一化内容指标会忽略部分空格/标点，也可能掩盖布局错误；自动错误taxonomy只是候选症状。关闭OCR的空输出全部计0，没有删除失败。

共享模板、少量合成数据、单seed、复用历史baseline和非受控计时限制外推。未进行全参训练对照、真实PDF端到端字段验证、多机器模型复现或生产可靠性测试。未经授权上传真实文件可能泄露隐私；本项目发布材料只使用虚构输入，密钥留在忽略目录以外的私有凭据存储。发布扫描仅识别已知格式，不能证明没有所有隐私或密钥；未清理或改写Git历史，也未取得任何外部认证。

AI贡献、自动核验和待做人工工作见[披露](evidence/ai-usage.md)及[最终自查](reports/self-assessment.md)。后续计划优先补独立数据和人工检查，再讨论更大模型或应用集成。
