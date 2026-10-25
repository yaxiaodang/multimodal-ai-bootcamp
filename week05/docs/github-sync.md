# GitHub 同步｜首次推送已核验，收尾与草稿 PR 待发布

当前采用本人要求的 VS Code 终端方案。Codex 已恢复 HTTPS 推送地址，并移除本次添加的仓库专用 SSH 代理配置；原有私钥、公钥、GitHub 账号公钥和已核对的主机信任均保留。

- 分支：`codex/week05-document-ai`。
- Fetch / Push：`https://github.com/yaxiaodang/multimodal-ai-bootcamp.git`。
- 文件与学习记录均已本地提交，无需再执行 git add 或 git commit。
- 本人首次 HTTPS 推送已成功；Codex 读取远程分支，确认本地 HEAD、远程跟踪及 GitHub 分支均为 `51dd75cd5c2836099745d282bfaff5ca5ab5b505`。
- 当前新增收尾文档与发布入口需要再推送，草稿 PR 尚未创建。不能把已验证的首次推送写成这些后续提交也已上传。

## 当前操作：一次发布收尾提交并创建草稿 PR

Codex 当前进程无法复用 VS Code 的登录。已准备 [publish_github.py](../scripts/publish_github.py)，请在已登录 GitHub 的 VS Code Remote SSH 内置终端、仓库根目录执行：

```bash
.venv/bin/python week05/scripts/publish_github.py
```

作用：只推送已提交的第五周分支，核对远程提交与本地一致，再复用 Git 正常认证入口创建或查找指向 main 的草稿 PR；输出实际 PR 地址。不会提交工作区文件、强制推送或合并 main。其他周已有的未提交文件不会被加入此次发布。

脚本通过 git credential fill 复用 VS Code askpass / 已配置 helper，授权仅用于 GitHub API 请求内存，不显示或写入文件；没有登录或权限不足时明确报错，不写作 PR 已创建。无需在聊天中提供凭据。执行结果只把提交号、PR URL 等非凭据信息保存在 `.git/week05-publish-receipt.json`，供 Codex 核验。

若出现登录提示，在 VS Code/浏览器完成授权。完成后把终端输出发给 Codex，Codex 将核对并关联实际 PR；合并需在可审阅的 PR 准备好后另行处理。

准备检查入口（由 Codex 执行，不需要本人重复）：

```bash
.venv/bin/python week05/scripts/publish_github.py --prepare-only
```

作用：检查当前分支、HTTPS 推送地址、已提交状态及 PR 正文；不推送、不读取凭据、不调用 API。

如需单独推送或核对：

```bash
git push -u origin codex/week05-document-ai
```

作用：上传当前分支已提交内容，建立远程跟踪，不创建 PR。

```bash
git ls-remote --heads origin refs/heads/codex/week05-document-ai
```

作用：只读获取远程分支提交号，供与本地比较。

## 已完成的排查

1. HTTPS：Codex 非交互进程没有可用凭据；本人在 VS Code 内置终端的首次推送成功，当前 Codex 进程的非交互推送仍因没有凭据失败。
2. SSH 主机信任：已根据 GitHub 官方 Ed25519 指纹核对并追加主机密钥，严格校验通过。
3. SSH 账号公钥：本人添加后服务器已接受公钥。
4. SSH 本机签名：现有私钥有口令加密；本人多次输入得到 Bad passphrase，表示忘记口令，故改用 HTTPS。没有覆盖旧密钥或生成替代密钥。
5. 仓库配置：之前的 SSH 推送和专用代理设置已撤回，当前推送明确使用 HTTPS。

首次推送终端输出及 git ls-remote 的实际提交号匹配是成功证据；收尾提交和草稿 PR 仍需下一次执行结果。诊断见 [github-sync.json](../evidence/github-sync.json)。

官方说明：[VS Code GitHub 登录](https://code.visualstudio.com/docs/sourcecontrol/github#_sign-in-to-github-for-git-operations)、[GitHub 主机指纹](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)。

脚本接口参考：[Git credential](https://git-scm.com/docs/git-credential)、[GitHub PR API](https://docs.github.com/en/rest/pulls/pulls#create-a-pull-request)。
