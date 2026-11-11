"""Offline Capstone reproduction: authenticate inputs, rescore archives, audit release."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
WEEK = ROOT / 'week12'
sys.path.insert(0, str(ROOT))


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def same_metrics(actual, expected):
    # Python 3.12+ improves float summation; accept rounding noise only.
    # IDs, strings, counts, booleans, keys and list order must still agree exactly.
    if isinstance(actual, float) and isinstance(expected, float):
        return math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(same_metrics(actual[k], expected[k]) for k in actual)
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(same_metrics(a, b) for a, b in zip(actual, expected))
    return type(actual) is type(expected) and actual == expected


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def authenticate():
    manifest = read('week12/evidence/manifest.json')
    if not manifest['files']:
        raise ValueError('Empty evidence manifest')
    for name, expected in manifest['files'].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or sha(path) != expected:
            raise ValueError(f'Frozen evidence changed: {name}')
    return manifest


def results():
    # Use the frozen Week07 scoring, never the printed report as ground truth.
    from week10.scripts.common import pdf_rows, verify, aggregate
    config = read('week12/configs/capstone.json')
    protocol, docs = verify()
    if config['pdf_protocol'] != 'week10/configs/protocol.json' or config['pdf_test'] != 'week07/data/test-manifest.json':
        raise ValueError('Unsupported scoring protocol; version the experiment before changing it')
    suite = read(config['pdf_suite'])
    pdf = {}
    for label, folder in [('ocr-on', protocol['pdf_baseline']), ('ocr-off', suite['pdf_no_ocr'])]:
        rows, _ = pdf_rows(ROOT / folder, docs)
        pdf[label] = {'source': folder, 'overall': aggregate(rows),
                      'types': {kind: aggregate([r for r in rows if r['type'] == kind])
                                for kind in ['digital', 'scan', 'table']}}
    from week08.train import score
    text = {label: score(read(folder + '/predictions.json')) for label, folder in suite['text'].items()}
    # Week11's independent archive checker authenticates these mechanism receipts.
    lora = read('week11/reports/comparison.json')
    if lora['suite'] != config['lora_suite']:
        raise ValueError('LoRA suite differs from Capstone configuration')
    return {'scope': 'Archived predictions rescored; no new inference or training',
            'pdf': pdf, 'text_reserved_test': text,
            'lora_validation': {r: {k: v[k] for k in ['trainable_parameters', 'adapter_bytes',
                                'frozen_base_equal', 'reload_equal', 'merge_greedy_equal', 'after']}
                                for r, v in lora['results'].items()},
            'error_cases': len(read('week10/reports/error-taxonomy.json')),
            'human_review': 'pending', 'peer_reproduction': 'pending',
            'decision': 'Keep OCR for mixed PDFs; text adapters remain teaching candidates.'}


def result_markdown(value):
    lines = ['# 从原始归档重算的结果', '',
             '本页由 `week12/run.py` 的评分函数生成；本周没有重新训练或推理。', '',
             '| PDF方法 | 页数 | 内容相似度 | 顺序 | 表格严格匹配 | 扫描内容相似度 |',
             '| --- | --- | --- | --- | --- | --- |']
    for label, data in value['pdf'].items():
        a = data['overall']
        lines.append(f"| {label} | {a['n']} | {a['score']:.6f} | {a['reading_order']:.6f} | {a['table_exact']:.0%} | {data['types']['scan']['score']:.6f} |")
    lines += ['', '| 英文文本方法 | 预留测试条数 | JSON严格正确率 |', '| --- | --- | --- |']
    for label, data in value['text_reserved_test'].items():
        lines.append(f"| {label} | {data['n']} | {data['exact_rate']:.0%} |")
    lines += ['', f"Week10保留{value['error_cases']}个方法×文档错误候选；本人复核、同学复现待完成。",
              'PDF与英文文本是两项任务；两张表不支持跨任务排名。完整证据和成本见[最终报告](final-report.md)。', '']
    return '\n'.join(lines)


def release_audit():
    inventory = read('week12/evidence/release-files.json')
    # Scan the intended release, not ignored local caches or unrelated uncommitted work.
    patterns = {
        'github_token': rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
        'huggingface_token': rb'hf_[A-Za-z0-9]{30,}',
        'openai_project_key': rb'sk-proj-[A-Za-z0-9_-]{30,}',
        'aws_access_id': rb'AKIA[A-Z0-9]{16}',
        'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    }
    findings, large, missing = [], [], []
    sizes = []
    for name in inventory['files']:
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError('Release path escapes repository')
        if not path.is_file():
            missing.append(name)
            continue
        if path.name in {'.env', '.netrc', 'id_rsa', 'id_ed25519'} or path.suffix in {'.pem', '.key'}:
            findings.append({'file': name, 'rule': 'credential_filename'})
        size = path.stat().st_size
        sizes.append((size, name))
        if size > inventory['max_file_bytes']:
            large.append({'file': name, 'bytes': size})
        blob = path.read_bytes()
        for rule, pattern in patterns.items():
            if re.search(pattern, blob):
                findings.append({'file': name, 'rule': rule})
    return {'passed': not (findings or large or missing), 'scope': 'Listed release working files; no Git history scan',
            'files_scanned': len(inventory['files']), 'findings': findings, 'oversize': large, 'missing': missing,
            'largest_files': [{'file': p, 'bytes': s} for s, p in sorted(sizes, reverse=True)[:5]],
            'limitation': 'Pattern screening cannot prove absence of all credentials or private/unauthorized documents; source cards and human checks still required.'}


def local_links():
    checked = 0
    sources = list(WEEK.rglob('*.md'))
    sources += [ROOT / 'README.md']
    for source in sources:
        if 'dist' in source.parts:
            continue
        for match in re.finditer(r'\[[^\]]*\]\(([^)]+)\)', source.read_text(encoding='utf-8')):
            target = match[1].split('#')[0]
            if not target or re.match(r'[a-zA-Z]+:', target):
                continue
            if not (source.parent / target).is_file():
                raise ValueError(f'Broken local link: {source.relative_to(ROOT)} -> {target}')
            checked += 1
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', action='store_true', help='Audit, then export the committed HEAD as a tar.gz release (requires Git)')
    args = parser.parse_args()
    tick = time.monotonic()
    execution = {'started_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
                 'platform': platform.platform(), 'commands': [], 'status': 'running',
                 'human_review': 'pending', 'new_training': False, 'new_inference': False}
    output = WEEK / 'evidence'
    output.mkdir(exist_ok=True)
    try:
        manifest = authenticate()
        for label, script in [('week10', 'week10/scripts/verify.py'), ('week11', 'week11/scripts/verify.py')]:
            cmd = [sys.executable, script]
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                  timeout=read('week12/configs/capstone.json')['timeout_seconds_per_audit'])
            (output / f'{label}-audit.log').write_text(proc.stdout + proc.stderr, encoding='utf-8')
            execution['commands'].append({'argv': ['python3', script], 'exit_code': proc.returncode,
                                          'log': f'week12/evidence/{label}-audit.log'})
            if proc.returncode:
                raise ValueError(f'{label} audit failed; see audit log')
        value = results()
        if not same_metrics(value, read('week12/reports/results.json')):
            raise ValueError('Recomputed metrics differ from released results.json')
        if result_markdown(value) != (WEEK / 'reports/results.md').read_text(encoding='utf-8'):
            raise ValueError('Results table differs from raw scores')
        audit = release_audit()
        dump(output / 'release-audit.json', audit)
        if not audit['passed']:
            raise ValueError('Release audit failed; see release-audit.json (values redacted)')
        execution.update({'frozen_files_checked': len(manifest['files']), 'local_links_checked': local_links(),
                          'pdf_pages_per_method': 24, 'text_test_per_method': 12, 'status': 'passed'})
        if args.package:
            # Refuse to package an older committed version while checking newer working files.
            inventory = read('week12/evidence/release-files.json')
            for name in inventory['files']:
                committed = subprocess.run(['git', 'show', f'HEAD:{name}'], cwd=ROOT, capture_output=True, check=True).stdout
                if committed != (ROOT / name).read_bytes():
                    raise ValueError(f'Commit release changes before packaging: {name}')
            package = WEEK / 'dist/capstone.tar.gz'
            package.parent.mkdir(exist_ok=True)
            subprocess.run(['git', 'archive', '--format=tar.gz', '-o', str(package), 'HEAD'], cwd=ROOT, check=True)
            execution['package'] = {'path': str(package.relative_to(ROOT)), 'sha256': sha(package), 'bytes': package.stat().st_size}
        print(result_markdown(value))
        print('PASS: archived results reproduced; human and peer checks remain pending.')
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        execution['status'] = 'failed'
        execution['error'] = str(error)
        print(f'Capstone audit refused: {error}', file=sys.stderr)
    finally:
        execution['elapsed_seconds'] = time.monotonic() - tick
        dump(output / 'execution.json', execution)
    return 0 if execution['status'] == 'passed' else 2


if __name__ == '__main__':
    sys.exit(main())
