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
| 参数规模 | 约 67M（6700 万参数，官方模型页面显示） | 约 0.8B |
| CPU 适配度 | 适合本周实验 | 本机未验证；需核对依赖、内存需求并实际测试 |
| Intended Use | 英文情感分类 | 图像理解、文档问答等 |
| Limitations | 英文、二分类、反讽理解有限 | OCR、幻觉、复杂版面及资源需求 |
| Week 2 是否运行 | 是 | 否 |

## 选择结论与验证范围

- 本周运行 DistilBERT：它与英文情感分类任务匹配，
  已在当前 Ubuntu 虚拟机的 CPU 环境中完成推理。
- Qwen 作为后续图像与文本理解任务的候选模型，
  本周仅进行资料对比，没有实际运行。
- 当前未验证 Qwen 在本机的加载速度、推理速度、
  内存占用以及表单问答效果。
- 两者用途不同，本表不构成同一任务上的性能比较。
