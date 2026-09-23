# 12 周自主学习日志

每周记录实际完成的工作、遇到的问题、解决方法，以及下一步任务。运行结果以仓库中的代码、Notebook 和输出文件为准。

## Week 01：环境与可复现性基础

### 已完成

- 建立 `multimodal-ai-bootcamp` 仓库和 Python 虚拟环境。
- 编写环境检查、测试图片生成和图片信息读取代码。
- 使用 Pillow 读取测试图片的宽度、高度和格式。
- 编写自动化测试；在 `week01/` 目录运行 `python -m pytest -q`，结果为 `3 passed`。
- 将第一周文件整理进 `week01/`，并保留项目根目录的总览文件和依赖文件。

### 遇到的问题与解决

文件移动到 `week01/` 后，直接运行 `pytest -q` 曾出现 `ModuleNotFoundError: No module named 'src'`。调整测试运行方式后，在 `week01/` 目录使用 `python -m pytest -q` 验证通过。

### 本周收获

理解了虚拟环境、项目目录、依赖记录和自动化测试的作用。周文件夹用于整理学习产物；Git 分支用于隔离一段尚未合并的工作，两者解决的是不同问题。

## Week 02：Hugging Face 与 CPU 推理

### 本周目标

学习如何查看模型与数据集信息，固定模型版本，在 CPU 上完成一次推理，并保存可检查的结果与失败案例。

### 已完成

- 学习 Hugging Face 的模型、Model Card、模型版本和 Pipeline 等基础概念。
- 创建 `week02/transformers-demo.ipynb`，选择项目 `.venv` 内核运行。
- 使用模型 `distilbert/distilbert-base-uncased-finetuned-sst-2-english`。
- 将模型版本固定为 `714eb0fa89d2f80546fda750413ed43d93601a13`，并指定 CPU 运行。
- 运行 3 条正常文本、1 条反讽文本和 1 条无效输入，将 5 条记录保存到 `week02/predictions.jsonl`。
- 编写 `week02/run-metadata.yaml` 和 `week02/failure-case.md`。

### 运行环境与观察

本次 Notebook 输出的环境为 Python 3.10.12、PyTorch 2.14.0+cpu、Transformers 5.17.0、huggingface_hub 1.32.0；CUDA 不可用。

正常样例分别得到正面、负面和负面分类。反讽句 “Great, another two-hour delay. Just what I needed.” 得到 `POSITIVE`，分数约为 `0.993`；按语境阅读，这句话表达的是负面态度。整数 `12345` 不是有效文本输入，程序记录了 `ValueError`。

这些是少量样例的观察结果，不能当作模型整体准确率。

### 遇到的问题与解决

Ubuntu 虚拟机起初无法访问 Hugging Face，模型加载时反复请求 `config.json` 并报网络不可达。Windows 能访问网站，但虚拟机和 Jupyter 内核需要分别检查网络设置。配置可用的网络代理后，Notebook 成功访问模型文件并完成 CPU 推理。

使用 Notebook 时还需要区分 Markdown 单元和代码单元：说明文字放在 Markdown 单元，Python 语句放在代码单元；运行代码前确认选择了正确的 `.venv` 内核。

### 我目前的理解

- 模型 ID 用来指定模型；固定的 revision 用来指明本次使用的具体版本。
- Pipeline 把模型加载和推理步骤组合起来，但仍需要核对任务、输入和输出。
- 分类分数反映模型对其输出标签的分数；反讽案例说明高分结果仍可能与人的语境判断不一致。
- 无效输入造成的程序错误，与模型对有效输入判断错误，是两类不同的问题。
- 没有独立显卡也可以完成本周的 CPU 推理；首次下载模型仍依赖网络。

### 待完成

- [ ] 核对并完成 `model-comparison.md`。
- [ ] 完成所选数据集的调查记录，核对实际文件名及引用信息。
- [ ] 完成一项进一步探索，并保存实际操作与结果。
- [ ] 重启 Notebook 内核，从头运行全部单元，核对输出文件。
- [ ] 检查 `week02/README.md`、运行信息和依赖记录是否与实际一致。
- [ ] 提交 Week 2 分支，并在合并后记录完成情况。

完成一项再勾选一项；如果实验结果与预期不同，把实际结果写在这里。