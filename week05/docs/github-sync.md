# GitHub 同步｜收尾推送已核验，PR 待创建

当前采用本人要求的 VS Code 终端方案。Codex 已恢复 HTTPS 推送地址，并移除本次添加的仓库专用 SSH 代理配置；原有私钥、公钥、GitHub 账号公钥和已核对的主机信任均保留。

- 分支：`codex/week05-document-ai`。
- Fetch / Push：`https://github.com/yaxiaodang/multimodal-ai-bootcamp.git`。
- 文件与学习记录均已本地提交，无需再执行 git add 或 git commit。
- 首次推送 51dd75c 已核验；本人随后运行发布入口，成功推送收尾提交 `a87d468297d737e306a30db1246672e1a3f9ea95`。Codex 独立核验 GitHub、远程跟踪与当时本地 HEAD 全部一致。
- 原发布入口在推送后的 ls-remote 检查失败并丢失错误细节，因此没有进入 PR 创建。独立重试核验成功，原失败原因未知，不归因于未经证实的网络问题。
- 已修复入口：以正常 Git 认证取得授权后，通过 GitHub Git refs API 核验远程提交，再创建或复用 PR；Git 检查错误显示遮盖凭据后的具体细节。仅该修复与说明尚待推送，草稿 PR 尚未创建。

## 当前操作：一次发布收尾提交并创建草稿 PR

Codex 当前进程无法复用 VS Code 的登录。已准备 [publish_github.py](../scripts/publish_github.py)，请在已登录 GitHub 的 VS Code Remote SSH 内置终端、仓库根目录执行：

```bash
.venv/bin/python week05/scripts/publish_github.py
```

作用：只推送已提交的第五周分支，复用 Git 正常认证入口，通过 GitHub Git refs API 核对远程提交与本地一致，再创建或查找指向 main 的草稿 PR；输出实际 PR 地址。不会提交工作区文件、强制推送或合并 main。其他周已有的未提交文件不会被加入此次发布。

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

两次成功推送均有终端输出及独立 git ls-remote 核验。入口修复的模拟检查见 [publish-preparation.txt](../evidence/publish-preparation.txt)，不把模拟 PR 当成实际创建结果；草稿 PR 仍待已登录终端执行。诊断见 [github-sync.json](../evidence/github-sync.json)。

官方说明：[VS Code GitHub 登录](https://code.visualstudio.com/docs/sourcecontrol/github#_sign-in-to-github-for-git-operations)、[GitHub 主机指纹](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)。

脚本接口参考：[Git credential](https://git-scm.com/docs/git-credential)、[GitHub PR API](https://docs.github.com/en/rest/pulls/pulls#create-a-pull-request)。

远程核验接口：[Get a reference](https://docs.github.com/en/rest/git/refs#get-a-reference)。本文件记录本次发布前状态，执行后的实际提交与 PR 地址以回执和 GitHub 页面为准。
