# GitHub 同步｜改用 VS Code 的 HTTPS 登录

当前采用本人要求的 VS Code 终端方案。Codex 已恢复 HTTPS 推送地址，并移除本次添加的仓库专用 SSH 代理配置；原有私钥、公钥、GitHub 账号公钥和已核对的主机信任均保留。

- 分支：`codex/week05-document-ai`。
- Fetch / Push：`https://github.com/yaxiaodang/multimodal-ai-bootcamp.git`。
- 文件与学习记录均已本地提交，无需再执行 git add 或 git commit。
- 当前尚未确认上传成功；待本人在 VS Code 交互登录并推送，再由 Codex 核对远程提交。

## 当前操作

如果旧终端仍停留在 Bad passphrase 提示，按 Ctrl+C 结束 ssh-add。本人的现有私钥有口令加密，已经表示忘记口令，不再重复尝试。

在 VS Code 通过 Remote SSH 连接 Ubuntu，打开本仓库，使用 VS Code 内置终端执行：

```bash
cd /home/yaxiaodang/multimodal-ai-bootcamp
```

作用：将工作目录从 Desktop 等其他位置切换到本仓库，确保推送正确项目。

```bash
git push -u origin codex/week05-document-ai
```

作用：通过 HTTPS 上传已经提交的第五周分支，并建立远程跟踪。此操作不依赖 Python 或 Conda 环境，不使用 SSH 私钥，不强制推送，不合并 main。其他周未提交的文件不会被此次推送自动加入提交。

如果 VS Code 提示登录 GitHub，允许打开浏览器并用有仓库写权限的账号完成授权，再回到 VS Code。基础 GitHub 登录与 Git 操作由 VS Code 内置支持，无需为此次推送安装额外的 PR 扩展。若终端只显示 Username/Password 或其他错误，保留提示文本供继续排查，不在聊天中发送凭据。

本人将推送终端结果发回后，Codex 再核对远程分支与本地 HEAD 是否一致。可用只读命令：

```bash
git ls-remote --heads origin refs/heads/codex/week05-document-ai
```

作用：读取远程分支提交号，供与本地提交比较，不修改仓库。

## 已完成的排查

1. HTTPS：Codex 非交互进程没有可用凭据；VS Code 的交互认证是另一执行环境，本轮需实际验证。
2. SSH 主机信任：已根据 GitHub 官方 Ed25519 指纹核对并追加主机密钥，严格校验通过。
3. SSH 账号公钥：本人添加后服务器已接受公钥。
4. SSH 本机签名：现有私钥有口令加密；本人多次输入得到 Bad passphrase，表示忘记口令，故改用 HTTPS。没有覆盖旧密钥或生成替代密钥。
5. 仓库配置：之前的 SSH 推送和专用代理设置已撤回，当前推送明确使用 HTTPS。

这里不把换到 VS Code 终端本身当作认证成功；需要浏览器授权及实际推送结果作为证据。诊断见 [github-sync.json](../evidence/github-sync.json)。

官方说明：[VS Code GitHub 登录](https://code.visualstudio.com/docs/sourcecontrol/github#_sign-in-to-github-for-git-operations)、[GitHub 主机指纹](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)。
