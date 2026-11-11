# Week08 invoice-text LoRA adapters

用途：本地CPU上的小规模PEFT/SFT教学。输入英语合成账单文本，输出JSON字符串字段total和currency。不接受图像/PDF，不是Docling或Qwen视觉adapter。

基础模型：HuggingFaceTB/SmolLM2-135M，revision `93efa2f097d58c2a74874c7e644dbc9b0cee75a2`，base license Apache-2.0。数据为本仓库新合成CC0-1.0文本。使用基础模型需遵循其许可证与模型卡。

两份adapter采用r=8、alpha=16、q_proj/v_proj、seed42、FP32、60步，A lr0.001，B lr0.0005；保存格式为PEFT safetensors。配置与精确位置见[报告](training-report.md)。加载需保持相同基础模型revision和tokenizer；[train.py](train.py)内含完整保存后重加载验证，不需要合并权重。

训练只使用96条train；同12条validation进行训练前后对比。reserved-test未做模型评价，Week07 PDF测试集未参与训练或超参选择。每条预测和失败均保存。结果只支持同模板合成文本，不能代表真实票据表现；模板与币种完全相关是已知偏差。

不适用于真实账单自动审批、财务核算、未知格式、OCR噪声、中文、缺失字段或多币种复杂文档。即使输出可解析，也可能包含错误数值，需要对照原文。不得据此声称视觉能力或PDF解析能力提升。

开发与验证：Codex代写代码、执行实验及自动检查；本人人工核验尚待完成。具体证据、资源和限制见[训练报告](training-report.md)，本人工作见[收尾清单](reports/manual-review.md)。
