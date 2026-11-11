# 本人最后完成：登录、同步、Report与人工核验

可自动执行的实验已代执行。以下步骤需要你的账号与本人判断。Ubuntu VM通过VS Code Remote SSH连接时，命令仍在远端终端执行，浏览器可用本机浏览器。不要把API key发给聊天或写进仓库。

## 1. 阅读和抽查（无需重训）

- [ ] 阅读[README](../README.md)与[实测报告](report.md)，能够讲出“唯一变量、数据不变、同指标、产物与结论关联”。
- [ ] 打开comparison.json指向的A/B目录，各抽查至少3条after-predictions.json，另看1条baseline失败。对照answer和prediction，确认JSON字段评分符合直觉。
- [ ] 区分SDK启动失败、summary导出失败与主动中断演练；主动演练不证明自然训练不稳定。
- [ ] 看curves.png，能说明loss/NLL降低与任务exact不是同一个概念；小验证集同分不证明泛化。

## 2. 登录W&B并选择真实entity

```bash
cd ~/multimodal-ai-bootcamp
```

作用：进入Ubuntu仓库根目录，找到本机原生离线记录和缓存。

```bash
.venv-week08/bin/wandb login
```

作用：用你自己的W&B账号在终端交互登录；按提示到浏览器获取凭据，仅在终端输入，不在命令参数、代码、截图或学习记录中保存key。凭据由SDK保存在本机用户配置，不属于仓库。

在W&B网页确认实际账号/团队slug，下面将 `YOUR_ENTITY` 换成该值；不要假定它等于GitHub用户名。若需私有项目，先在网页建名为 `multimodal-ai-bootcamp-week09` 的项目并选择Private，再同步。

```bash
.venv-week08/bin/python week09/scripts/sync_cloud.py --entity YOUR_ENTITY
```

作用：只打印将要执行的各条sync命令，不上传；检查project和具体离线目录。首次SDK启动失败无有效ID，不会上传。

```bash
.venv-week08/bin/python week09/scripts/sync_cloud.py --entity YOUR_ENTITY --sync
```

作用：上传本机所有有有效ID的W&B离线runs（包括summary导出失败run）及artifact，不重新训练；随后从W&B API读取实际run URL、状态和artifact带版本的名字，保存为 `week09/reports/cloud-links.json`。网络或凭据错误时非零退出，日志保留，修复后可重试；不要手写:v0冒充实际版本。

注意：同步前不要删除 `week09/wandb/`、`.cache-week09/`。本机缓存不在Git中；全新clone先重跑实验生成新spool和ID。若sync提示找不到文件，检查当前VM缓存，不要把已有JSON当作可同步原生记录。

## 3. 创建网页W&B Report

- [ ] 在W&B项目确认A/B正常结束，failure-drill为失败状态且带intentional-failure标签，核对ID和learning_rate。
- [ ] 在Workspace比较A/B：横轴 `train/step`，面板为 `train/loss`、`validation/answer_nll`、`resource/process_rss_mib`；查看summary的after/exact_rate、training_seconds、peak_rss_mib。
- [ ] 打开Artifacts，抽查dataset、code、model和evaluation，核对digest与run ID；本实验用metadata关联input，不额外声称云端消费边。
- [ ] 从Workspace的Create report选择图表，或从项目Reports → Create report创建报告，将[report.md](report.md)的实验问题、结果、限制、失败与下一步复制过去，加入A/B图表和run引用，选择Filter run sets以固定报告中的实验集合。将开头的“离线未同步”状态改成实际状态，补上真实云端标识。界面按钮若更新，以当前页面为准。
- [ ] 保存/发布Report，按需要保留项目/报告的私有权限，复制Report链接。

```bash
.venv-week08/bin/python week09/scripts/sync_cloud.py --entity YOUR_ENTITY --sync --report-url 'https://wandb.ai/替换为实际Report链接'
```

作用：核对云端runs和artifact，并把你刚创建的实际Report URL写入cloud-links.json；传入完整真实链接，不使用示例文字。原始离线identity.json保留运行时状态，不手工改写。

## 4. 补齐学习记录并保存收尾结果

- [ ] 根目录learning-log.md：填写本人实际投入时间、理解/疑问、人工抽查样例ID、自评，添加project/run/artifact version/Report链接，更新仍为“待补”的完成状态。
- [ ] 不用把真实密钥、.netrc、原生W&B debug日志或用户配置加入Git。

```bash
git add learning-log.md week09/reports/cloud-links.json
git commit -m 'docs(week09): record verified cloud runs artifacts and report'
git push origin codex/week09-wandb
```

作用：依次暂存人工补齐的记录与云端标识、生成收尾提交、推送到本周分支。仅在cloud-links.json真实生成且已核验后执行；若手动改了report.md，可显式加入该文件。不要用git add .混入其他周尚未提交的工作。
