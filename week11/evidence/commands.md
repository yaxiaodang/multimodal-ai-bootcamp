# 执行命令与作用

所有路径以Ubuntu仓库根目录为基准；用户可复制的主入口见[README](../README.md)。下表说明AI本轮实际使用的主要命令类别，不要求你逐条重做。

| 命令/形式 | 作用与影响 |
| --- | --- |
| `pwd`、`rg --files`、`rg -n ...`、`cat ...`、`sed -n ...`、`tail ...` | 确认目录、快速查文件/字段、读取现有说明和运行日志；不改变实验 |
| `git status --short`、`git log -5 --oneline`、`git remote -v` | 核对已有修改、来源提交和目标仓库，避免混入其他周工作 |
| `git ls-remote https://github.com/microsoft/LoRA.git HEAD` | 查询官方代码当前commit；本轮核对并固定c4593f0，后续使用固定链接 |
| `git ls-remote --heads origin` | 读取目标仓库分支，检查网络；只读，不推送 |
| `gh auth status` | 检查本机GitHub授权；不在仓库保存token；沙箱内网络受限时返回invalid，联网环境复查成功 |
| `gh pr list --repo yaxiaodang/multimodal-ai-bootcamp --state open ...` | 只读检查现有PR，避免重复 |
| `mkdir -p week11/...` | 创建本周配置、脚本、结果和报告目录 |
| `python3 -m py_compile week11/run.py week11/scripts/*.py` | 检查脚本语法，不加载模型；生成的pycache被Git忽略 |
| `python3 week11/run.py --verify-only` | 核验冻结输入和rank单变量配置，打印哈希，不训练 |
| `git switch -c codex/week11-paper-reproduction` | 从当前Week10提交建立Week11分支；保留既有工作区修改 |
| `git add week11/experiment-plan.md week11/configs week11/run.py week11/scripts` | 仅暂存事前计划、配置和脚本 |
| `git commit -m 'feat(week11): preregister ...'` | 实验前建立计划提交863c77f，使事前标准可以核对 |
| `.venv-week08/bin/python week11/run.py` | 使用已有Python3.10 CPU环境顺序新训练r4/r8，检查机制并生成报告；自动子命令及退出码在suite.json |
| `python3 week08/scripts/test_metrics.py` | 运行复用指标的边界测试，确认额外字段/围栏等失败处理 |
| `python3 week11/run.py --check-archive` | 不加载模型，检查SHA、60步日志、重加载/合并文本及原始指标，输出verification.json |
| `git diff --check` | 检查补丁空白问题 |
| `git add week11 README.md learning-log.md` | 只暂存本周归档与根目录两个学习入口文件；本轮开始时这两个根文件无用户未提交改动 |
| `git commit -m 'feat(week11): archive ...'` | 将实际预测、adapter、报告和记录形成归档提交 |
| `git push -u origin codex/week11-paper-reproduction` | 将本周分支保存到用户指定GitHub仓库并设置upstream；不合并main |

系统限制：本轮默认沙箱将`.git`设为只读且限制联网。Git写入与GitHub联网使用受审批环境完成；模型训练和数据处理仍在当前CPU工作区离线运行。没有要求你提供新的凭据或为此重配SSH。
