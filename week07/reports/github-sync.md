# GitHub 保存说明

目标仓库：[yaxiaodang/multimodal-ai-bootcamp](https://github.com/yaxiaodang/multimodal-ai-bootcamp)。本周分支：`codex/week07-benchmark`，从现有第6周成果继续，确保相对路径引用的数据、Pipeline和模型证据存在。提交范围只含本周目录、根README入口与learning-log新增节；现有前几周未提交修改继续保留。

GitHub 上切换到 [本周分支](https://github.com/yaxiaodang/multimodal-ai-bootcamp/tree/codex/week07-benchmark) 查看。此次保存不自动合并main。

以下为归档命令与作用，Codex会在实验完成后执行，本人无需重复运行：

```bash
git add week07 README.md learning-log.md
git commit -m "feat(week07): freeze document benchmark and archive baseline evaluation"
git push -u origin codex/week07-benchmark
```

- `git add`：只暂存本周新增目录和两个索引/记录文件，不暂存旧周的未提交修改。
- `git commit`：把暂存的实验代码、配置、数据、原始输出与报告保存为本地版本。
- `git push -u`：上传当前本周分支并设置远程跟踪；不会合并main或强制覆盖远程历史。

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/codex/week07-benchmark
```

作用：分别读取本地提交和远程本周分支提交；两者一致才可确认当前提交已同步。最终提交号以本轮交付消息和Git历史为准。GitHub登录通过已有正常认证流程使用，无凭据写入仓库。
