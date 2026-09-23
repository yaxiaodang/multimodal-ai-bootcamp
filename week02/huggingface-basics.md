# Hugging Face Hub 基础学习笔记

## 1. 本阶段目标

从官方页面判断模型或数据集是否适合实验，而不是只根据模型名称、参数量或排行榜进行选择。

## 2. Hugging Face Hub 的主要组成

### Model Repository

用于保存模型权重、配置文件、Model Card、版本历史和官方使用示例。

### Dataset Repository

用于保存数据集、字段信息、数据划分、Dataset Card 和版本历史。

### Space

用于展示在线交互应用。Space 是演示程序，不等同于模型仓库。

### Library Documentation

用于说明 Transformers、Datasets 和 huggingface_hub 等 Python 库的使用方法。

## 3. Hub 与 Transformers 的区别

Hugging Face Hub 是模型、数据集和应用的托管与版本管理平台。

Transformers 是用于下载、加载和运行模型的 Python 库。

## 4. Model Card 阅读清单

- Model ID：
- Revision：
- Task：
- License：
- Inputs：
- Outputs：
- Requirements：
- Intended Use：
- Limitations：
- Evaluation：

## 5. Dataset Card 阅读清单

- Dataset ID：
- 创建者：
- 数据来源：
- License：
- Revision：
- Train/Validation/Test 划分：
- 字段：
- 语言：
- 模态：
- 样本数量：
- 隐私风险：
- 已知偏差：
- 已知质量问题：

## 6. Revision 的作用

Revision 用于指定模型或数据仓库的明确版本，通常记录 commit hash 或明确的 tag。

只记录模型 ID 而不记录 revision，模型仓库更新后，相同代码可能下载不同文件，导致实验无法准确复现。

## 7. License 的作用

模型或数据能够下载，不代表能够任意使用。使用前需要确认是否允许学习、研究、商业使用和重新分发。

## 8. 模型缓存与 Git

大型模型权重保存在 Hugging Face 本地缓存中，不提交到 Git。

Git 应保存：

- 模型 ID；
- revision；
- license；
- 运行配置；
- 输入；
- 原始输出；
- 依赖版本；
- 运行时间和设备；
- 失败案例。

## 9. Token 安全

- 不把 Hugging Face Token 写进 Python 代码；
- 不把 Token 写进 Notebook；
- 不把 Token 写进 YAML；
- 不把 Token 提交到 Git；
- 公开模型通常不需要登录；
- gated 或私有资源才需要授权。

## 10. 模型页面示例无法运行时的排查顺序

1. 检查 Model ID；
2. 检查 revision；
3. 检查模型是否 gated；
4. 检查是否需要登录；
5. 检查 Transformers 和 PyTorch 版本；
6. 检查 tokenizer 或 processor；
7. 检查输入格式；
8. 检查 CPU、内存或显存；
9. 保存原始错误信息后再修改环境。

## 11. 当前环境约束

- 操作系统：Ubuntu 虚拟机
- Python：3.10.12
- 虚拟环境：项目根目录 `.venv`
- 运行设备：CPU
- 独立显卡：无
- GitHub：可通过 Windows 代理访问
- Hugging Face：可通过 Windows 代理访问

## 12. 尚未解决的问题

1. 如何从模型页面获得准确的 commit hash？
2. 如何估算一个模型的内存需求？
3. 如何判断 Model Card 中的评测结果是否适用于自己的任务？