# 最后由本人完成的操作

可以先读完报告，最后集中执行。空白是待办，不代表实验已经人工确认。

| 待办 | 怎么做/记录什么 | 当前状态 |
| --- | --- | --- |
| 抽查原始证据 | 从final-report打开扫描PDF及表格PDF，对照reference与原始JSON；至少核对一个OCR失败、一个结构失败、一个英文字段成功和base失败。在Week10人工CSV填写核查者、判断、原因 | 待本人 |
| 核对学习理解 | 能用自己的话解释“为何保留OCR”“表格strict为何独立”“12条全对为何不证明泛化”；本人补learning-log实际时间/还不理解/自主阶段 | 待本人 |
| 五分钟展示 | 按demo.md练习或录制，写下日期、实际时长、一个听众问题、自己的回答；录像为可选，实际展示必做 | 待本人 |
| 邀请同学复现 | 把README的本周分支clone命令交给同学；记录系统、Python、commit、命令、退出码、结果和改进建议 | 待同学，本人邀请 |
| 发布内容复核 | 抽查公开文件确为虚构/授权内容，理解模式扫描的范围；不上传私人账单、凭据或完整模型 | 待本人 |
| 旧周账号收尾 | 如需补齐Week09，按其README登录W&B、同步A/B离线run并创建Report，回填entity、artifact vN与Report链接；本周不自动代登录 | 待本人 |

同学复现记录：日期____；姓名/匿名代号____；环境____；commit____；退出码____；看到的关键数字____；困难与反馈____；对应Issue/日志____。

演示记录：日期____；时长____；最可信结论____；最重要限制____；听众问题与回答____。

本人最终判断：是否采用OCR默认方案____；是否生产采用英文adapter及理由____；当前自主阶段____；下一步首先做____。

GitHub本周分支已可供查看。若今后把本地个人修改同步到远端，在Ubuntu终端执行：

```bash
git status --short
git add learning-log.md week12/reports/manual-review.md week12/reports/self-assessment.md week10/reports/manual-review.csv
git commit -m "docs(week12): record personal review and peer reproduction"
git push
```

作用：依次检查改动、仅暂存本次个人记录、生成可追溯提交、推送当前已关联的本周分支。先确认暂存范围只包含自己完成的记录；涉及静态报告的修改需要同步维护manifest或另写追加记录。未要求合并main，现有分支成果可直接交付。
