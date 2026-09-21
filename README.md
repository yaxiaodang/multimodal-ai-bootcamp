# Multimodal AI Bootcamp

这是我的 12 周多模态视觉智能课程仓库。Week 1 的目标是建立一个可以从空环境复现的研究工程。

## Week 1 工具

`image_info.py` 用于读取单张图片，并输出：

- 图片路径；
- 图片宽度；
- 图片高度；
- 图片格式。

## 支持环境

- Ubuntu Linux
- Python 3.10–3.12
- CPU 即可
- 不需要 GPU

## 1. 克隆仓库

```bash
git clone https://github.com/yaxiaodang/multimodal-ai-bootcamp.git
cd multimodal-ai-bootcamp
```

在 Week 1 Pull Request 合并之前，复现对应分支：

```bash
git switch week01-research-workflow
```

## 2. 创建并激活虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 4. 唯一开始命令

```bash
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

预期结果：

```text
3 passed
```

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
- 学习记录：`learning-log.md`
- 环境信息：`evidence/environment-output.txt`
- 成功输出：`evidence/success-output.txt`
- 错误输出：`evidence/error-output.txt`
- 测试输出：`evidence/test-output.txt`
- 复现记录：`docs/reproducibility_notes.md`
- Pull Request：[Week 1 Pull Request](https://github.com/yaxiaodang/multimodal-ai-bootcamp/pull/1)