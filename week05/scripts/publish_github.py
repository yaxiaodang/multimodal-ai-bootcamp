"""在已登录的 VS Code 终端推送第五周、核对远程提交并创建或复用草稿 PR。"""

import argparse
import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
REPO = 'yaxiaodang/multimodal-ai-bootcamp'
BRANCH = 'codex/week05-document-ai'
REMOTE = f'https://github.com/{REPO}.git'
TITLE = 'Week 5: Document AI task map and controlled layout comparison'
BODY = ROOT / 'week05/reports/pull-request.md'


def git(*args):
    result = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, timeout=45)
    if result.returncode:
        detail = re.sub(r'(https?://)[^/\s@]+@', r'\1[redacted]@', result.stderr.strip())
        detail = re.sub(r'\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)', '[redacted]', detail)
        raise RuntimeError(f'Git 检查失败：{args[0]}（exit={result.returncode}）：{detail[-1200:]}')
    return result.stdout.strip()


def preflight():
    if git('branch', '--show-current') != BRANCH:
        raise RuntimeError(f'请在 {BRANCH} 分支执行，不自动切换分支。')
    if git('remote', 'get-url', '--push', 'origin') != REMOTE:
        raise RuntimeError('推送地址与本项目 HTTPS 地址不一致，停止。')
    if git('status', '--porcelain', '--untracked-files=all', '--',
           'week05', 'learning-log.md', 'README.md'):
        raise RuntimeError('本周文件仍有未提交改动，请先交由 Codex 整理提交。')
    body = BODY.read_text(encoding='utf-8')
    if not body.strip():
        raise RuntimeError('PR 正文为空。')
    return git('rev-parse', 'HEAD'), body


def github_credential():
    # 复用 Git 正常的 credential helper / VS Code askpass，不读取其他凭据文件。
    result = subprocess.run(
        ['git', 'credential', 'fill'], cwd=ROOT,
        input=f'protocol=https\nhost=github.com\npath={REPO}.git\n\n',
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
        env=dict(os.environ, GIT_TERMINAL_PROMPT='0'), timeout=180,
    )
    if result.returncode:
        raise RuntimeError('无法从 Git 认证入口取得授权，请在已登录的 VS Code 内置终端执行。')
    fields = dict(line.split('=', 1) for line in result.stdout.splitlines() if '=' in line)
    if not fields.get('password'):
        raise RuntimeError('Git 未返回可用于 GitHub API 的授权，请检查 VS Code GitHub 登录。')
    return fields['password']


def github_api(token, path, payload=None, method=None):
    request = Request(
        'https://api.github.com' + path,
        data=json.dumps(payload).encode('utf-8') if payload is not None else None,
        headers={'Authorization': 'Bearer ' + token,
                 'Accept': 'application/vnd.github+json',
                 'Content-Type': 'application/json',
                 'User-Agent': 'multimodal-ai-bootcamp-week05'},
        method=method,
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        # 不回显请求头或完整认证响应，仅保留去除凭据的错误消息。
        try:
            message = str(json.load(error).get('message', ''))
        except (ValueError, AttributeError):
            message = ''
        message = message.replace(token, '[redacted]')[:300]
        raise RuntimeError(f'GitHub API 返回 HTTP {error.code}：{message}；已推送的分支会保留。') from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true',
                        help='只核对分支、远程地址和文件；不推送、不获取凭据、不调用 API')
    args = parser.parse_args()
    try:
        head, body = preflight()
        print(f'分支：{BRANCH}\n本地提交：{head}', flush=True)
        if args.prepare_only:
            print('准备检查通过；未推送、未读取凭据、未创建 PR。')
            return 0
        print('推送已提交的第五周文件……', flush=True)
        result = subprocess.run(['git', 'push', '-u', 'origin', BRANCH], cwd=ROOT)
        if result.returncode:
            raise RuntimeError('推送失败，请将终端错误发给 Codex。')
        print('分支推送完成。通过 GitHub API 核对远程提交……', flush=True)
        token = github_credential()  # 仅在内存中使用，不输出、不保存。
        remote = github_api(token, f'/repos/{REPO}/git/ref/heads/{BRANCH}')
        if remote.get('object', {}).get('sha') != head:
            raise RuntimeError('远程提交与本地不一致，停止创建 PR。')
        receipt = {'verified_at': datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(),
                   'branch': BRANCH, 'local_head': head, 'remote_head': head,
                   'push_verified': True, 'verification_method': 'GitHub Git refs API',
                   'pull_request_url': None}
        receipt_path = Path(git('rev-parse', '--git-path', 'week05-publish-receipt.json'))
        if not receipt_path.is_absolute():
            receipt_path = ROOT / receipt_path
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('远程提交核对一致。准备创建或复用草稿 PR……', flush=True)
        query = urlencode({'state': 'open', 'head': 'yaxiaodang:' + BRANCH, 'base': 'main'})
        existing = github_api(token, f'/repos/{REPO}/pulls?' + query)
        if existing:
            pr = existing[0]
            if pr.get('title') != TITLE or pr.get('body') != body:
                pr = github_api(token, f'/repos/{REPO}/pulls/{pr["number"]}',
                                {'title': TITLE, 'body': body}, method='PATCH')
        else:
            pr = github_api(token, f'/repos/{REPO}/pulls',
                            {'title': TITLE, 'head': BRANCH, 'base': 'main',
                             'body': body, 'draft': True})
        url = pr.get('html_url', '')
        if not url.startswith(f'https://github.com/{REPO}/pull/'):
            raise RuntimeError('GitHub 返回的 PR 地址不符合预期，停止。')
        receipt.update(pull_request_url=url, pull_request_number=pr['number'],
                       draft=pr.get('draft'), merged=pr.get('merged', False))
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'PR：{url}\n同步与 PR 准备完成，请将以上输出发给 Codex。')
        return 0
    except (OSError, ValueError, RuntimeError, URLError, subprocess.TimeoutExpired) as error:
        print(f'收尾未全部完成：{error}')
        print(f'手动 PR 入口：https://github.com/{REPO}/compare/main...{BRANCH}?expand=1')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
