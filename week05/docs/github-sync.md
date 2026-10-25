# GitHub 同步修复｜待账号添加认证公钥

2026-10-25，本人明确要求解决同步。Codex 已检查当前分支和远程地址，核对并追加 GitHub 官方 Ed25519 主机密钥，保留 known_hosts 原记录；只将本仓库推送地址切换为 SSH，拉取地址仍为 HTTPS。未生成或覆盖个人密钥。

- 分支：`codex/week05-document-ai`。
- Fetch：`https://github.com/yaxiaodang/multimodal-ai-bootcamp.git`。
- Push：`git@github.com:yaxiaodang/multimodal-ai-bootcamp.git`。
- 主机信任：已修复；严格检查通过。
- 账号认证：尚未成功，GitHub 对本机 id_ed25519 公钥返回 `Permission denied (publickey)`。当前进程没有可用的 SSH 代理连接；直接指定现有密钥仍被服务器拒绝，因此本次阻塞不能只归因于代理。
- 推送状态：尚未成功。需要在有仓库写权限的 GitHub 账号中添加或核对该公钥的认证用途，之后由 Codex 继续验证和推送。

## 账号持有人完成的一步

在 Ubuntu Remote SSH 终端执行：

```bash
cat ~/.ssh/id_ed25519.pub
```

作用：显示现有公钥，便于复制到 GitHub；无需生成新密钥。仅复制 `.pub` 文件输出的完整一行。

登录有仓库写权限的账号，打开 [New SSH key](https://github.com/settings/ssh/new)，Title 可填 ubuntu-vm，Key type 选择 Authentication Key，Key 粘贴完整公钥并保存。若该公钥已添加，应核对账号及用途；如提示 Key already in use，保留提示并告知 Codex，不覆盖现有密钥。

这一步需要本人登录 GitHub 账号，当前环境没有可用的 HTTPS 凭据或 GitHub 登录会话，Codex 无法代为完成账号认证。完成后告知 Codex，由 Codex 继续执行以下步骤。

## 后续验证与推送（由 Codex 执行）

```bash
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -T git@github.com
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
