# GitHub 同步修复｜公钥已接受，待本机解锁

2026-10-25，本人明确要求解决同步。Codex 已检查当前分支和远程地址，核对并追加 GitHub 官方 Ed25519 主机密钥，保留 known_hosts 原记录；只将本仓库推送地址切换为 SSH，拉取地址仍为 HTTPS。未生成或覆盖个人密钥。

- 分支：`codex/week05-document-ai`。
- Fetch：`https://github.com/yaxiaodang/multimodal-ai-bootcamp.git`。
- Push：`git@github.com:yaxiaodang/multimodal-ai-bootcamp.git`。
- 主机信任：已修复；严格检查通过。
- 账号公钥：本人已添加，后续 SSH 日志出现 Server accepts key，表明 GitHub 已接受现有公钥。最初的拒绝状态已解决。
- 本机签名：现有私钥有口令加密，不能在无交互模式下自行解锁。Codex 已启动专用代理 `~/.ssh/bootcamp-github-agent.sock`，并仅为当前仓库设置 core.sshCommand 使用该代理与现有密钥；未更改全局 Git 配置。
- 推送状态：尚未成功；现在仅需本人在自己的终端解锁私钥，然后由 Codex 完成认证与推送。

## 当前唯一操作：本人解锁现有私钥

```bash
SSH_AUTH_SOCK=/home/yaxiaodang/.ssh/bootcamp-github-agent.sock ssh-add ~/.ssh/id_ed25519
```

作用：连接已准备的专用代理，按终端提示输入现有私钥口令，把密钥加入代理供当前仓库签名认证。该命令前的变量只用于此次 ssh-add；当前仓库已另行指定相同代理。看到 Identity added 后告知 Codex。口令只在本人终端输入，不写入文档或聊天。

代理没有跨虚拟机重启持久保存解锁状态；重启后如需同步，应重新启动代理并解锁。


## 已完成的账号公钥添加（历史排查步骤）

在 Ubuntu Remote SSH 终端执行：

```bash
cat ~/.ssh/id_ed25519.pub
```

作用：显示现有公钥，便于复制到 GitHub；无需生成新密钥。仅复制 `.pub` 文件输出的完整一行。

登录有仓库写权限的账号，打开 [New SSH key](https://github.com/settings/ssh/new)，Title 可填 ubuntu-vm，Key type 选择 Authentication Key，Key 粘贴完整公钥并保存。若该公钥已添加，应核对账号及用途；如提示 Key already in use，保留提示并告知 Codex，不覆盖现有密钥。

本人已告知添加完成，服务器随后接受公钥；当前无需重复添加。下面保留步骤供排查查阅。

## 后续验证与推送（由 Codex 执行）

```bash
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o IdentityAgent=/home/yaxiaodang/.ssh/bootcamp-github-agent.sock -o IdentitiesOnly=yes -i /home/yaxiaodang/.ssh/id_ed25519 -T git@github.com
```

作用：验证主机信任与 GitHub SSH 账号身份；成功会显示 Hi 用户名。GitHub 不提供交互 Shell，成功认证时命令退出码通常为 1，应结合消息判定。

```bash
git push -u origin codex/week05-document-ai
```

作用：上传该分支的现有提交并建立远程跟踪；不强制推送，不合并 main，不包含工作区未提交的其他周文件。

```bash
git ls-remote --heads origin refs/heads/codex/week05-document-ai
```

作用：读取远程分支提交号，与本地 HEAD 比较，确认同步结果；这是只读检查。

## 信任依据与证据

GitHub 官方 Ed25519 主机指纹为 `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`，用于核对服务器身份，不是本人的认证公钥。证据见 [同步诊断](../evidence/github-sync.json)。

官方说明：[主机密钥指纹](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)、[添加账号 SSH 公钥](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)。
