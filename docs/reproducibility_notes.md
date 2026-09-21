# Week 1 复现记录

## 复现信息

- 复现日期：2026-09-21
- 操作系统：Ubuntu Linux
- Python 版本：Python 3.10.12
- Git 分支：`week01-research-workflow`
- 复现方式：全新 clone + 全新 venv
- 复现目录：`~/multimodal-ai-bootcamp-repro`

## 执行命令

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/create_sample.py
python src/image_info.py samples/demo.png
python -m pytest -q
python src/image_info.py samples/not-found.png
```

## 复现结果

- 成功创建独立 Python 虚拟环境；
- 成功安装 `requirements.txt` 中声明的依赖；
- 成功生成 640×480 的 PNG 测试图片；
- 图片工具正确输出宽度、高度和格式；
- 自动化测试结果为 `3 passed`；
- 不存在的文件能够返回清晰错误信息；
- 错误输入的退出码为 `2`。

## 遇到的问题

本次全新 clone 和空虚拟环境复现未遇到阻塞性问题。

## 解决方法

本次复现无需额外修改，README 中的安装和运行命令可以直接执行。

## 当前限制

- 当前仅处理单张图片；
- 不支持 PDF；
- 不执行 OCR；
- 不支持目录批量处理；
- 尚未完成跨操作系统复现。

## 同伴复现与审查

- 复现人：何睿宁
- 复现平台：ubuntu
- 是否成功：成功
- 具体反馈：VS Code 曾检测到已有环境并尝试创建 `.venv-1`。通过检查解释器路径，
最终固定使用项目目录中的 `.venv`，避免不同环境之间的依赖混淆。
- 反馈处理结果：运行成功