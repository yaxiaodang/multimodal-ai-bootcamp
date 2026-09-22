# Multimodal AI Bootcamp

本仓库用于记录多模态视觉 AI 12 周自主学习路线的代码、实验配置、原始结果、失败案例和学习总结。

## 学习环境

- 操作系统：Ubuntu 虚拟机
- 开发工具：Windows VS Code + Remote SSH
- Python：3.10.12
- 虚拟环境：`.venv`
- 主要设备：CPU

## 目录结构

| 目录或文件 | 说明 |
|---|---|
| `week01/` | 可复现研究工程 |
| `week02/` | Hugging Face 与模型推理 |
| `week03/` | AI 辅助编程与人工验证 |
| `week04/` | 视觉语言模型 |
| `week05/` | Document AI 任务地图 |
| `week06/` | Docling 文档解析 Pipeline |
| `week07/` | Dataset、Benchmark 与负责任使用 |
| `week08/` | LoRA/PEFT 小规模微调 |
| `week09/` | W&B 实验追踪 |
| `week10/` | 统一评测、消融与错误分析 |
| `week11/` | 论文导读与最小复现 |
| `week12/` | Capstone、展示与自主答辩 |
| `learning-log.md` | 12 周连续学习记录 |
| `requirements.txt` | 项目累计 Python 依赖 |
| `.venv/` | 本地 Python 虚拟环境，不提交 Git |

## 初始化环境

```bash
cd ~/multimodal-ai-bootcamp
source .venv/bin/activate
python -m pip install -r requirements.txt