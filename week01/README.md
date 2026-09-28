# Multimodal AI Bootcamp

这是我的 12 周多模态视觉智能课程仓库。Week 1 的目标是建立一个可以从空环境复现的研究工程。

## Week 1 工具

`image_info.py` 用于读取单张图片，并输出：

- 图片路径；
- 图片宽度；
- 图片高度；
- 图片格式。

## 支持环境

- 已验证：Ubuntu Linux、Python 3.10.12、CPU
- Python 3.11 和 3.12：尚未在本仓库留下验证记录
- 不需要 GPU

## 1. 克隆仓库

```bash
git clone https://github.com/yaxiaodang/multimodal-ai-bootcamp.git
cd multimodal-ai-bootcamp
```

以下步骤使用当前 `main` 版本。Week 1 当时的改动与审查记录见 [PR #1](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/1)。

## 2. 创建并激活虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. 安装依赖

在仓库根目录执行，因为 `requirements.txt` 位于根目录：

```bash
python -m pip install -r requirements.txt
```

## 4. 唯一开始命令

先进入 `week01/`，再生成样例并检查图片：

```bash
cd week01
python scripts/create_sample.py && python src/image_info.py samples/demo.png
```

预期结果：

```text
file: samples/demo.png
width: 640
height: 480
format: PNG
```

## 查看帮助

```bash
python src/image_info.py --help
```

## 运行测试

```bash
python -m pytest -q
```

当前 `main` 版本预期有 **9 项测试通过**；测试耗时可能因环境而异。Week 1 当时只有 3 项测试，其原始输出保存在 `evidence/test-output.txt`。Week 3 扩充了同一工具的测试，因此当前结果与历史记录不同。

## 验证错误输入

```bash
python src/image_info.py samples/not-found.png
```

程序应提示文件不存在，并返回非零退出码。

## 数据来源

测试图片由 `scripts/create_sample.py` 自动生成，不包含个人信息、第三方素材或未授权数据。

## 项目结构

- `src/`：图片信息工具源代码
- `scripts/`：测试图片生成脚本
- `tests/`：自动化测试
- `docs/`：项目计划和复现记录
- `evidence/`：环境及运行原始输出
- `samples/`：生成的测试图片

## 已知限制

- 当前仅处理单张图片；
- 不支持 PDF；
- 不执行 OCR；
- 不支持目录批量处理；
- 当前主要在 Ubuntu 环境验证。

## Week 1 证据

- 项目计划：`docs/project_plan.md`
- 学习记录：[根目录 learning-log.md](../learning-log.md)
- 依赖版本：[根目录 requirements.txt](../requirements.txt)
- 环境信息：`evidence/environment-output.txt`
- 成功输出：`evidence/success-output.txt`
- 错误输出：`evidence/error-output.txt`
- 测试输出：`evidence/test-output.txt`
- 复现记录：`docs/reproducibility_notes.md`
- Pull Request：[Week 1 Pull Request](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/1)
- 自主探索：`docs/reproducibility_concepts.md`