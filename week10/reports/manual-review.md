# 本人最后完成的操作

AI已代执行实验与自动核验。你最后完成阅读、人工检查与真实学习记录；无需重新训练。

1. 阅读[主线说明](../README.md)和[实测报告](evaluation-report.md)，能解释为什么PDF和英文账单不能混排，为什么高内容相似度仍可能表格不合格。
2. 打开[错误表](error-taxonomy.md)，先不看自动标签，抽查至少6个case：PDF基线表格、PDF基线扫描、no-OCR扫描失败、no-OCR数字页成功，以及base英文抽取失败、adapter英文成功。成功对照在comparison.json/runs中，错误表只包含失败。
3. 对照原PDF、参考结构和实际document.json/document.md；英文对照原text、answer和prediction。在[manual-review.csv](manual-review.csv)填写human_labels、confirmed、notes，记录与自动分类不一致处。抽查不能冒充全部错误都已确认。
4. 在根目录learning-log.md Week10补实际学习小时数、理解困惑、你做的人工核验与自主阶段。AI运行耗时不等于你的学习耗时。
5. W&B账号操作沿用[Week09本人收尾](../../week09/reports/manual-review.md)：登录、同步已存在的A/B离线run，核对真实artifact版本，创建/更新网页Report，把本周两个任务的表格、错误和采用决定加入报告。将真实project/run/artifact :vN/Report链接填回学习记录；本周未创建新的W&B评测run，不填写不存在的ID。禁止把API key写入仓库。

若需从Ubuntu命令行核验：

```bash
python3 week10/scripts/verify.py
```

作用：不联网、不加载模型地核对归档文件哈希并从原始预测重新计算指标；不能替代人工看原页。

若自行更新人工复核后保存到GitHub：

```bash
git status --short
git add learning-log.md week10/reports/manual-review.csv
git commit -m "docs(week10): record personal review and learning reflections"
git push
```

作用依次为：检查哪些文件变更；只暂存学习记录与人工复核；创建本地提交；上传当前分支。若同时填写了Report链接所在的其他文档，应把具体文件加入git add；不要使用git add .收走其他周尚未提交的编辑。
