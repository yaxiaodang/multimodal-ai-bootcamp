# Week 02 数据集调查：FUNSD

## 1. 本次调查范围

- Hugging Face 数据集：[nielsr/funsd](https://huggingface.co/datasets/nielsr/funsd)。
- 原始项目：[FUNSD: Form Understanding in Noisy Scanned Documents](https://guillaumejaume.github.io/FUNSD/)。
- 调查方式：查看公开数据集页面、仓库元数据与原始项目介绍；本周**没有下载数据集，也没有训练或评测文档模型**。
- 数据集版本：本次尚未记录仓库的完整 commit SHA。页面信息反映查看时的状态；以后实际运行实验，应记录数据集 revision。

## 2. 它能用来做什么

FUNSD 是表单理解数据集。每份样本包括扫描的表单图像，以及与文字及其位置有关的标注。可以用它研究文档中的文字识别、版面信息和字段含义，例如辨认表单中的问题与回答。原始项目介绍了 199 张已标注表单。

它与本项目的多模态文档方向有关：模型需要结合图像、文字和位置理解页面。Week 02 的 DistilBERT Notebook 处理的是英文句子的情感分类；它没有使用 FUNSD，也不能直接完成 FUNSD 的表单理解任务。

## 3. 页面上能核对的数据

| 项目 | 观察到的信息 |
| --- | --- |
| 数据集 ID | `nielsr/funsd` |
| 模态 | 图像、文字 |
| 划分 | `train`：149 条；`test`：50 条；合计 199 条 |
| 页面展示的文件格式 | Parquet |
| 本次是否下载数据 | 否 |
| 本次是否运行数据集实验 | 否 |

Hugging Face 仓库元数据列出的每条样本字段如下：

| 字段 | 本周的理解 |
| --- | --- |
| `id` | 样本标识 |
| `image` | 表单图像 |
| `words` | 从表单得到的词语序列 |
| `bboxes` | 与词语对应的位置框序列 |
| `ner_tags` | 与词语对应的类别标签序列 |

`ner_tags` 的类别名称在仓库元数据中列为：`O`、`B-HEADER`、`I-HEADER`、`B-QUESTION`、`I-QUESTION`、`B-ANSWER`、`I-ANSWER`。`B-` 表示一类片段的开始，`I-` 表示同类片段的后续词；`O` 表示不属于这些标记类别。原始 FUNSD 还介绍了实体之间的关联；上表列的是 **这个 Hugging Face 版本展示的字段**，不能假定它包含原始格式中的全部关联信息。

## 4. 使用前需要确认的事

1. **许可与用途**：`nielsr/funsd` 的数据集页面没有明确给出可直接确认的许可证。另一个介绍原始 FUNSD 的项目说明它用于非商业研究和教育，但这不能替代对当前数据集副本及原始来源条款的核对。本周只调查页面；今后公开发布数据或用于其他用途之前，先核查授权与引用要求。
2. **标注质量与适用范围**：样本量只有 199 条，表单来自特定来源；不能仅凭这个数据集推断模型对所有语言、所有表单的表现。原始数据集的标签也曾被后续研究讨论和修订。
3. **版本可复现**：本次没有固定数据集 commit SHA；如果后续下载并进行实验，要先记下所用 revision、下载方式和实际样本划分。
4. **数据与推理任务不同**：本周的 `transformers-demo.ipynb` 使用固定版本的文本情感分类模型，不读取本数据集；两者的结果不能混写成同一次实验。

## 5. 本周结论与下一步

本周完成了**数据集页面调查**：知道 FUNSD 提供表单图像、词语、位置框和类别标签，并能说明它与文档理解的关系。尚未实际下载或查看本地样本，因而没有本地样本截图、加载耗时、训练结果或模型指标。

若后续课程需要基于 FUNSD 做实验，再按顺序完成：核对许可及来源 → 记录数据集完整 revision → 下载并检查样本字段 → 选择与文档理解任务相符的模型 → 记录真实运行结果。

## 参考来源

- [Hugging Face：nielsr/funsd 数据集页面](https://huggingface.co/datasets/nielsr/funsd)
- [Hugging Face：nielsr/funsd 仓库元数据](https://huggingface.co/datasets/nielsr/funsd/blob/main/README.md)
- [原始 FUNSD 项目页](https://guillaumejaume.github.io/FUNSD/)
- [FUNSD Datasets 项目对原始数据的说明](https://github.com/crcresearch/FUNSD)
