# Multimodal AI Bootcamp

本仓库用于记录多模态视觉 AI 12 周自主学习路线的代码、实验配置、原始结果、失败案例和学习总结。

## 最终项目开始入口

在Ubuntu远端终端、仓库根目录执行：

```bash
python3 week12/run.py
```

作用：仅用Python3.10+标准库，从已归档原始输出重算24页PDF的OCR对照、12条英文文本测试并核对LoRA证据；不联网、不下载模型、不训练。先读[Week12学习入口](week12/README.md)、[最终报告](week12/reports/final-report.md)和[Project Card](week12/project-card.md)。模型再次训练/推理的环境另见对应周；陌生同学复现与本人展示待完成。

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
| [week04/](week04/README.md) | 视觉语言模型：受控实验、双维度评价、五个失败案例与缓存复现 |
| [week05/](week05/README.md) | Document AI 任务地图：分步学习入口与实验准备（实验待执行） |
| [week06/](week06/README.md) | Docling 文档解析 Pipeline：主线、10项核验与Markdown/JSON表示探索已完成 |
| [week07/](week07/README.md) | Dataset、Benchmark 与负责任使用：24页冻结测试集、Docling baseline、切片评测与最差五例 |
| [week08/](week08/README.md) | LoRA/PEFT：CPU字段抽取SFT、训练前后对比、学习率对照与adapter归档 |
| [week09/](week09/README.md) | W&B实验追踪：CPU A/B、原生离线runs、artifact与报告；账号同步及网页Report待本人收尾 |
| [week10/](week10/README.md) | 统一评测：24页PDF关闭OCR消融、base/A/B独立文本测试、42个错误case与成本报告；人工复核待本人 |
| [week11/](week11/README.md) | 论文导读与最小复现：LoRA Paper Card、事前计划、CPU rank4/8新训练与合并核验；本人阅读/复核待收尾 |
| [week12/](week12/README.md) | Capstone：设计卡、Project Card、离线重算、可复现实验包、五分钟演示与答辩材料；本人/同学收尾待做 |
| `learning-log.md` | 12 周连续学习记录 |
| `requirements.txt` | 项目累计 Python 依赖 |
| `.venv/` | 本地 Python 虚拟环境，不提交 Git |

## 初始化环境

```bash
cd ~/multimodal-ai-bootcamp
source .venv/bin/activate
python -m pip install -r requirements.txt
```

根目录依赖清单用于基础工具；第四周 CPU 推理依赖与完整实验入口见 [Week 4 README](week04/README.md)，结果与限制见 [实验报告](week04/reports/report.md)。
