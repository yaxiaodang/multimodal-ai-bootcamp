"""运行三份 PDF 的 pdftotext 基线，保留原始文本与证据，不执行 OCR 或自动评分。"""

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return datetime.now(ZoneInfo('Asia/Shanghai'))


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def preflight(config_path):
    config = json.loads(config_path.read_text(encoding='utf-8'))
    if config['tool'] != 'pdftotext':
        raise ValueError('本入口只支持 pdftotext。')
    executable = shutil.which(config['tool'])
    if not executable:
        raise ValueError('缺少 pdftotext，请先安装系统包 poppler-utils。')
    version = subprocess.run([executable, '-v'], capture_output=True, check=True, timeout=10)
    version_text = (version.stdout + version.stderr).decode('utf-8', errors='replace')
    if not re.search(r'version\s+' + re.escape(config['expected_version']) + r'(?:\s|$)', version_text):
        raise ValueError('pdftotext 版本与配置不一致；请先核对环境，不静默更改版本。')
    manifest_path = ROOT / config['manifest']
    reference_path = ROOT / config['manual_expectations']
    plan_path = ROOT / config['evaluation_plan']
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    reference_path.read_text(encoding='utf-8')
    documents = manifest['documents']
    if not documents or len({item['id'] for item in documents}) != len(documents):
        raise ValueError('输入清单为空或文档 ID 重复。')
    for item in documents:
        if not re.fullmatch(r'[A-Za-z0-9_-]+', item['id']):
            raise ValueError('文档 ID 只能包含字母、数字、下划线和短横线。')
        if item['pages'] != [1]:
            raise ValueError('本轮配置只提取第 1 页；输入页码与配置不一致。')
        path = ROOT / item['path']
        if sha256(path) != item['sha256']:
            raise ValueError(f'输入 SHA-256 不一致：{item["id"]}，请先核对材料。')
    if not plan['checks'] or any(c['document_id'] not in {d['id'] for d in documents} for c in plan['checks']):
        raise ValueError('检查项为空或引用了清单外的文档。')
    return config, documents, plan, executable, version_text, [manifest_path, reference_path, plan_path]


def run(config_path, prepared):
    config, documents, plan, executable, version_text, source_paths = prepared
    started = now()
    run_dir = ROOT / 'runs' / f'baseline-{started:%Y%m%dT%H%M%S}-{uuid4().hex[:6]}'
    run_dir.mkdir(parents=True)
    snapshots = run_dir / 'snapshots'
    snapshots.mkdir()
    snapshot_files = [config_path, *source_paths, Path(__file__)]
    snapshot_info = []
    for source in snapshot_files:
        shutil.copyfile(source, snapshots / source.name)
        snapshot_info.append({'file': source.name, 'sha256': sha256(source)})
    version = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    status = subprocess.run(['git', '-C', str(ROOT), 'status', '--porcelain'], capture_output=True, text=True)
    metadata = {
        'status': 'running', 'started_at': started.isoformat(), 'timezone': 'Asia/Shanghai',
        'python': sys.version.split()[0], 'git_commit': version.stdout.strip() or None,
        'git_status': status.stdout.splitlines(), 'tool_version': version_text,
        'config': config, 'snapshots': snapshot_info, 'documents': [],
        'evaluation': 'pending_user_review; no automatic score',
    }
    meta_path = run_dir / 'run-metadata.json'
    save_json(meta_path, metadata)
    (run_dir / 'tool-version.txt').write_text(version_text, encoding='utf-8')
    fields = ['check_id', 'document_id', 'dimension', 'expected', 'raw_output', 'judgment', 'evidence_location', 'reason']
    with (run_dir / 'review.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for check in plan['checks']:
            writer.writerow({'check_id': check['id'], 'document_id': check['document_id'],
                             'dimension': check['dimension'], 'expected': check['expected'],
                             'raw_output': f'{check["document_id"]}.txt'})
    print(f'输出目录：{run_dir}', flush=True)
    interrupted = False
    try:
        for item in documents:
            sample_id = item['id']
            output = run_dir / f'{sample_id}.txt'
            command = [executable, *config['arguments'], str(ROOT / item['path']), str(output)]
            record = {'id': sample_id, 'input': item['path'], 'input_sha256': item['sha256'],
                      'command': command, 'started_at': now().isoformat(), 'status': 'running'}
            metadata['documents'].append(record)
            save_json(meta_path, metadata)
            tick = time.monotonic()
            try:
                result = subprocess.run(command, capture_output=True, timeout=config['timeout_seconds_per_document'])
                stdout, stderr, exit_code = result.stdout, result.stderr, result.returncode
            except subprocess.TimeoutExpired as error:
                stdout, stderr, exit_code = error.stdout or b'', error.stderr or b'', None
                record['error'] = 'timeout'
            except OSError as error:
                stdout, stderr, exit_code = b'', str(error).encode('utf-8'), None
                record['error'] = type(error).__name__
            (run_dir / f'{sample_id}.stdout.log').write_bytes(stdout)
            (run_dir / f'{sample_id}.stderr.log').write_bytes(stderr)
            record.update({'finished_at': now().isoformat(), 'elapsed_seconds': round(time.monotonic() - tick, 6),
                           'exit_code': exit_code, 'status': 'completed' if exit_code == 0 and output.exists() else 'failed',
                           'output': output.name if output.exists() else None,
                           'output_bytes': output.stat().st_size if output.exists() else None,
                           'output_sha256': sha256(output) if output.exists() else None})
            save_json(meta_path, metadata)
            print(f'{sample_id}: {record["status"]}, exit={exit_code}, output_bytes={record["output_bytes"]}', flush=True)
    except KeyboardInterrupt:
        interrupted = True
        metadata['status'] = 'interrupted'
        for record in metadata['documents']:
            if record['status'] == 'running':
                record.update({'status': 'interrupted', 'finished_at': now().isoformat()})
    finally:
        if not interrupted:
            metadata['status'] = 'completed' if all(d['status'] == 'completed' for d in metadata['documents']) else 'failed'
        metadata['finished_at'] = now().isoformat()
        save_json(meta_path, metadata)
    print('原始 txt 未经改写；review.csv 留空待本人评价。退出码成功不等于内容正确。')
    return 130 if interrupted else (0 if metadata['status'] == 'completed' else 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'configs/baseline.json', help='基线配置路径')
    parser.add_argument('--prepare-only', action='store_true', help='只核对版本、输入哈希与参考文件，不提取正文、不创建运行目录')
    args = parser.parse_args()
    try:
        prepared = preflight(args.config)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(2, f'准备检查失败：{error}\n')
    if args.prepare_only:
        print(f'准备检查通过：{len(prepared[1])} 份 PDF，{len(prepared[2]["checks"])} 项待人工评价；未提取正文，未创建运行目录。')
        return 0
    return run(args.config, prepared)


if __name__ == '__main__':
    raise SystemExit(main())
