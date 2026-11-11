# Week 8 训练前计划（2026-11-11）

问题：在 Ubuntu CPU 上，短程 LoRA 能否让小语言模型更遵守文档金额字段的 JSON 输出格式？这是下游文本抽取教学实验，不是视觉模型或 Docling 微调。

已有 Week07 Docling baseline 用于 PDF 解析，与这里的语言模型任务、指标不同，不作数值比较。Week07 test 不读取、不训练、不调参。生产项目应先尝试规则、Prompt 和 pipeline；本任务可用规则解决，采用 LoRA 是为了学习训练证据链，没有证明微调是最佳工程方案。

模型：HuggingFaceTB/SmolLM2-135M，Apache-2.0，revision `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`。英语纯文本 base model，无 chat template，不接受图片。选择135M以适应约8GB CPU虚拟机，不直接训练Qwen3.5多模态模型。

数据：新生成虚构账单文本，96 train / 12 validation / 12 reserved test，ID和完整文本不重合，先冻结SHA-256。训练与验证共享有限模板，是同分布教学检查；reserved test本周不运行。无真人或真实票据，无Week07参考、预测或test派生样例。

固定 Prompt：要求仅输出 `{"total":"金额","currency":"币种"}`，正文包括 subtotal、tax、total，答案来自total而非重新求和。SFT只对答案及EOS计算交叉熵，Prompt标签屏蔽。

协议：训练前先落盘12条base validation生成结果和答案token平均NLL，再接入LoRA。训练后同样的12条输入、greedy解码、max_new_tokens=32、无后处理修复。主指标为两个字段均正确的严格JSON解析匹配率；辅助为JSON可解析率、两个字段各自准确率、答案token加权NLL。每个失败都保留原始预测。

实验A：r=8、alpha=16、q_proj/v_proj、dropout=0、lr=0.001、AdamW、batch=2、accumulation=2（有效batch=4）、max_steps=60、FP32、seed=42、CPU线程=2。每20步记录train/validation NLL，固定最后一步，不按验证选checkpoint。

探索B：只将learning_rate改为0.0005，其余完全一致，从相同base与LoRA初始化重新开始。只作一次seed的描述性比较，不因结果差继续搜索。不把生成格式改善等同于阅读理解或视觉能力提升。

成功标准：真实完成60步、仅adapter更新、保存可加载权重、前后评测及失败样例齐全。效果假设为字段完全正确率提升；若不提升或退化也完整汇报，流程成功不等于效果假设成立。

预算：本地CPU，GPU 0小时、付费0元；每run训练最多15分钟，超时或非有限loss停止并保存failure.json及已有日志，不自动扩大规模。每个run保存配置、代码/数据哈希、版本、git基底及dirty状态、参数数、耗时和进程峰值RSS。CPU确定性只在当前软件/硬件范围内成立。

官方依据：[课程Week08](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/00_12_Week_Bootcamp/#week-8lorapeft)、[后训练专题](https://multimodal-vision-ai.github.io/multimodal-document-ai-learning-center/learning/08_Post_Training/)、[模型卡](https://huggingface.co/HuggingFaceTB/SmolLM2-135M)、[PEFT Quicktour](https://huggingface.co/docs/peft/quicktour)、[LoRA参数](https://huggingface.co/docs/peft/package_reference/lora)。
