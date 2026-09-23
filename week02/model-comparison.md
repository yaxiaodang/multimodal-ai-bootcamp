# Week 2 模型对比

## 实验问题

在当前只有 CPU 的环境中，应该选择什么模型完成最小推理？视觉或多模态任务应该选择什么候选模型？

| 对比项 | CPU 小模型 | 多模态候选模型 |
|---|---|---|
| Model ID | distilbert/distilbert-base-uncased-finetuned-sst-2-english | Qwen/Qwen3.5-0.8B |
| Revision | 714eb0fa89d2f80546fda750413ed43d93601a13 | 2fc06364715b967f1860aea9cf38778875588b17 |
| Task | text-classification / sentiment-analysis | image-text-to-text |
| License | apache-2.0 | apache-2.0 |
| Inputs | 英文文本 | 图像和文本 |
| Outputs | POSITIVE/NEGATIVE 和 score | 生成文本 |
| 参数规模 | 待记录 | 约 0.8B |
| CPU 适配度 | 适合本周实验 | 可以尝试但本周不要求运行 |
| Intended Use | 英文情感分类 | 图像理解、文档问答等 |
| Limitations | 英文、二分类、反讽理解有限 | OCR、幻觉、复杂版面及资源需求 |
| Week 2 是否运行 | 是 | 否 |

为什么本周运行 DistilBERT，Qwen 适合后续哪类任务，以及目前没有实测 Qwen 的哪些性能。