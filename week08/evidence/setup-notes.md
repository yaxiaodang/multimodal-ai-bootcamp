# 环境准备过程

2026-11-11：普通沙箱网络不通；获准联网后下载公开模型及依赖。首次用系统 python3 建环境，因其为3.14，与既有Python3.10版PyTorch不兼容，import失败，尚未加载模型或开始训练。随后使用 `.venv/bin/python -m venv --clear .venv-week08` 重建为Python3.10；本周环境用bootcamp-base.pth复用既有 `.venv/lib/python3.10/site-packages`，PEFT/Accelerate安装在专用环境。不修改既有环境。此路径复用仅适用于当前虚拟机；全新复现按README独立安装。

模型缓存 `.cache-week08/hub`，固定revision，下载9个匹配文件。缓存和虚拟环境不提交，adapter提交。初始git分支创建受只读.git限制，获准后建立codex/week08-lora，旧周工作区改动原样保留。

首轮训练使用local_files_only仍触发Transformers/PEFT的adapter/config远程探测，日志中保留网络重试和配置查找警告；缓存权重加载成功，训练与重加载完成，没有发生失败训练。B及README复现命令设置HF_HUB_OFFLINE=1，避免网络探测；模型、初始化、数据、优化步骤与评价协议保持一致。A/B总耗时包含探测开销差异，不能直接归因于学习率。重建的venv中pip自行升级其setuptools，不影响旧venv。

联网复核GitHub登录有效，普通沙箱中的auth失败是网络限制，不需重新登录。
