# 环境准备过程

2026-11-11：普通沙箱网络不通；获准联网后下载公开模型及依赖。首次用系统 python3 建环境，因其为3.14，与既有Python3.10版PyTorch不兼容，import失败，尚未加载模型或开始训练。随后使用 `.venv/bin/python -m venv --clear .venv-week08` 重建为Python3.10；本周环境用bootcamp-base.pth复用既有 `.venv/lib/python3.10/site-packages`，PEFT/Accelerate安装在专用环境。不修改既有环境。此路径复用仅适用于当前虚拟机；全新复现按README独立安装。

模型缓存 `.cache-week08/hub`，固定revision，下载9个匹配文件。缓存和虚拟环境不提交，adapter提交。初始git分支创建受只读.git限制，获准后建立codex/week08-lora，旧周工作区改动原样保留。
