# Week 02：Hugging Face 模型推理与结果记录

本周目标：认识 Hugging Face 的模型与数据集页面，在没有独立显卡的 Ubuntu 虚拟机上完成一次 CPU 推理，并记录模型版本、运行环境、原始输出和失败案例。

本周运行的是英文情感分类模型。它用于练习模型加载和结果分析，不是文档图像识别模型。

## 当前进度

- [x] 学习 Hugging Face 基础概念。
- [x] 在 CPU 上运行固定版本的 DistilBERT 模型。
- [x] 保存 5 条输入的结果，包括正常输入、反讽案例和无效输入。
- [x] 编写 `run-metadata.yaml` 和 `failure-case.md`。
- [x] 核对并完成模型比较、数据集调查等其余笔记。
- [x] 完成所选的进一步探索，并记录实际结果。
- [x] 重启 Notebook 内核，从头运行全部单元并检查结果。
- [x] 完成 Week 2 的 Git 提交和合并。

勾选待办项之前，应先完成对应操作。

## 文件说明

| 文件 | 内容 |
| --- | --- |
| `transformers-demo.ipynb` | 环境检查、模型加载、CPU 推理及结果保存 |
| `predictions.jsonl` | Notebook 保存的 5 条输入及其运行结果 |
| `run-metadata.yaml` | 本次运行的模型、版本、设备及环境信息 |
| `failure-case.md` | 反讽误判和无效输入的分析 |
| `environment-freeze.txt` | 当时安装的 Python 软件包版本记录 |
| `huggingface-basics.md` | Hugging Face 基础学习笔记 |
| `model-comparison.md` | 模型比较笔记；按实际完成情况填写 |
| `dataset-review.md` | 数据集调查笔记；按实际完成情况填写 |

如果某个文件尚未创建，完成对应任务后再更新上表。进一步探索产生的文件，也请在创建后补充到这里。

## 已运行的模型

- 任务：英文文本情感分类。
- 模型：`distilbert/distilbert-base-uncased-finetuned-sst-2-english`。
- 固定版本：`714eb0fa89d2f80546fda750413ed43d93601a13`。
- 运行设备：CPU；Notebook 中 `DEVICE = -1`。
- 本次观察到的环境：Python 3.10.12、PyTorch 2.14.0+cpu、Transformers 5.17.0、huggingface_hub 1.32.0；CUDA 不可用。

完整运行信息以 `run-metadata.yaml` 和 Notebook 的实际输出为准。以上模型版本是本次推理使用的版本，不代表将来比较的其他模型版本。

## 如何查看和重跑

1. 在 VS Code 中打开项目根目录 `multimodal-ai-bootcamp`。
2. 打开 `week02/transformers-demo.ipynb`。
3. 选择项目的 `.venv` Python 内核。
4. 检查 Notebook 开头的网络代理设置是否仍适用于当前 Ubuntu 虚拟机。
5. 重启内核，按顺序运行全部单元。
6. 检查模型加载、5 条结果和 `week02/predictions.jsonl` 是否都正常生成。

项目根目录的 `requirements.txt` 当前记录的是 Week 1 的基础依赖；不能仅凭它重建本周的完整推理环境。Week 2 实际用到的软件包及版本请同时查看 `environment-freeze.txt`。完成本周收尾时，还需确认依赖安装步骤是否足够让新环境重跑 Notebook。

Notebook 开头包含在线连接检查。即使模型权重已经缓存，在断网状态下从头运行全部单元仍会在该检查处失败。离线探索应单独运行并记录，不要把离线检查结果当作 Notebook 全部单元运行成功的证据。

## 本次观察

Notebook 保存了 5 条记录：3 条正常文本、1 条反讽测试文本和 1 条无效输入。

- 普通正面句被判为 `POSITIVE`。
- 普通负面句被判为 `NEGATIVE`。
- 一条褒贬混合的句子被判为 `NEGATIVE`。
- “Great, another two-hour delay. Just what I needed.” 按人的理解带有负面反讽意味，模型却输出 `POSITIVE`，分数约为 `0.993`。高分不表示这个判断一定符合语境。
- 整数输入 `12345` 触发 `ValueError`；程序记录了错误，没有将其当作有效分类结果。

每条输入的原始输出和耗时见 `predictions.jsonl`。反讽案例的解释见 `failure-case.md`。

## 当前限制

- 本次只运行了英文情感分类模型，不能据此判断模型处理中文或文档图像的能力。
- 这里只检查了少量自选输入，不构成模型准确率评测。
- 首次下载模型需要 Ubuntu 虚拟机能够访问 Hugging Face；Windows 浏览器能够访问，不代表虚拟机或 Jupyter 内核也能访问。
- Notebook 中的代理地址与当前网络环境有关，换电脑或网络后需要重新检查。