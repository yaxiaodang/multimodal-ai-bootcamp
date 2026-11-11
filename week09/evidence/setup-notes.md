# Week09环境与执行异常

日期：2026-11-11（Asia/Shanghai）。沿用Week08 Python3.10.12环境与固定模型缓存，增加W&B0.31.0、Matplotlib3.10.9、psutil7.2.2，完整版本见requirements-lock.txt。普通沙箱联网安装因代理/socket限制失败，获准联网后安装完成；没有更改基础模型或Week08数据。

GitHub auth在普通沙箱报失败，获准联网后确认既有凭据有效，不需要用户重新登录。创建codex/week09-wandb分支，运行前计划与训练/追踪源码在a30ed31提交。其他周现有未提交改动保留，运行时metadata记录其存在，但W&B禁用自动Git diff捕获，artifact只加入明确文件。

首次W&B离线SDK启动因本机socket限制失败：run-a-20261111T073540Z，没有创建有效run ID、没有baseline或训练更新。failure.json、metadata与原始日志原样保留。获准沙箱外运行后保持offline模式，SDK本机服务正常，重新生成时间戳目录与ID。

未发现W&B环境变量或.netrc中的W&B凭据（只检查是否存在，不导出内容）。本轮不登录、不上传W&B、不购买服务。dataset/model许可继承Week08数据卡与模型revision。密钥、用户配置、原生spool和artifact缓存被Git忽略；小adapter、JSON导出和报告提交。

PEFT保存adapter时仍提示未找到基础模型config、假设词表未修改。由于固定本机基础模型/tokenizer已成功加载且本实验未增删词表，不更改模型协议；保存后通过重加载逐条预测一致性核验。

首次完整训练A（run-a-20261111T073611Z，ID hbzjq04o）完成预测及adapter重加载，但收尾导出dict(run.summary)遇到嵌套SummarySubDict无法JSON序列化，调度退出1。metadata中的complete记录的是训练阶段，不是追踪全流程；该目录不计入成功对照，未改写原始元数据。修复为显式导出普通JSON标量字典，提交4220d7c；先运行第2步失败演练核验收尾，再补跑A/B。原生SDK最终状态及出口码由verify.py核对。
