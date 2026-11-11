# 本人最后完成的操作

这部分需要你的实际阅读、判断和讲解；AI不代填完成状态。预计30–60分钟起，按实际情况记录，不把机器运行时间当学习时间。

## 1. 核对论文与代码（待本人）

- [ ] 打开[原文v2 §4.1](https://arxiv.org/html/2106.09685v2#S4.SS1)，用自己的话解释W₀/A/B/r，核对B零初始化与合并说明。
- [ ] 打开[原文§7.2](https://arxiv.org/html/2106.09685v2#S7.SS2)，确认小rank的证据和“不是每个任务都适用”的边界；不要求逐行推公式。
- [ ] 打开[官方Linear代码](https://github.com/microsoft/LoRA/blob/c4593f060e6a368d7bb5af5273b8e42810cdef90/loralib/layers.py#L110)，确认A Kaiming、B零；核对代码与原文的初始化差异。

本人阅读日期、理解或修订：待填。

## 2. 跑轻量核验并抽查（待本人）

在Ubuntu远端终端执行：

```bash
cd ~/multimodal-ai-bootcamp
python3 week11/run.py --check-archive
```

作用：进入仓库；核对现有归档SHA与原始预测评分，不重训、不联网。读`week11/evidence/verification.json`中的passed，不需要理解检查脚本细节。

- [ ] 打开[报告](reproduction-report.md)，确认机器核验结果和结论一致。
- [ ] 每rank至少抽两条（[案例](cases.md)已列出），从原始Prompt中的total/currency查到参考和模型输出，记录是否正确、是否只改了格式。
- [ ] 找到任一run的metadata.json中的冻结哈希和mechanism.json中的merge，解释为什么“值很接近”和“文本一致”分别要检查。

| rank / 样例ID | 原文金额与币种 | 训练前/后输出是否合理 | 本人备注 |
| --- | --- | --- | --- |
| r4 / F2000 | 待填 | 待填 | 待填 |
| r4 / F2001 | 待填 | 待填 | 待填 |
| r8 / F2000 | 待填 | 待填 | 待填 |
| r8 / F2001 | 待填 | 待填 | 待填 |

## 3. 学习记录与分享（待本人）

- [ ] 在根目录`learning-log.md` Week11填写自己的实际学习时间、仍不理解的问题、人工核验方式和自评；不要只因AI已运行就勾选“可解释”。
- [ ] 参考[五句话讲稿](meeting-notes.md)，脱稿解释问题、主张、证据、限制和本地结果。
- [ ] 如要标记人工复核完成，补日期、样例ID和结论，保留AI原始运行证据。

## 4. 保存个人复核（完成以上后）

```bash
git add week11/reports/manual-review.md learning-log.md
git commit -m "docs(week11): record personal paper and prediction review"
git push
```

作用：只暂存本人修改的复核与学习记录；建立可追踪提交；把当前分支提交同步到GitHub。不要使用`git add .`混入其他周未完成的修改。推送分支需已有upstream，本轮AI首次推送会设置；若从clone开始，先切换本周分支。
