"""解析固定 PDF 并保存原始 Markdown/JSON 与证据；人工判断保持空白。"""

import argparse
import csv
import hashlib
import importlib.metadata as packages
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[2]
WEEK = REPO / "week06"


def now():
    return datetime.now(ZoneInfo("Asia/Shanghai")).isoformat()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def repo_file(value):
    path = (REPO / value).resolve()
    if not path.is_relative_to(REPO):
        raise ValueError(f"路径必须位于仓库中：{value}")
    return path


def configure_environment():
    # Keep model caches inside this repository's ignored local directory.
    os.environ["HF_HOME"] = str(REPO / ".cache-week06/huggingface")
    os.environ["DOCLING_CACHE_DIR"] = str(REPO / ".cache-week06/docling")
    os.environ["OMP_NUM_THREADS"] = "2"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"


def pipeline_options(config):
    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions, TableFormerMode

    options = PdfPipelineOptions()
    options.artifacts_path = repo_file(config["artifacts_path"])
    options.accelerator_options = AcceleratorOptions(
        device=AcceleratorDevice.CPU, num_threads=config["num_threads"]
    )
    options.do_ocr = config["do_ocr"]
    options.ocr_options = RapidOcrOptions(
        lang=config["ocr_languages"], backend=config["ocr_backend"],
        force_full_page_ocr=config["force_full_page_ocr"]
    )
    if config.get("layout_revision"):
        options.layout_options.model_spec.revision = config["layout_revision"]
    options.do_table_structure = config["do_table_structure"]
    options.table_structure_options.mode = TableFormerMode(config["table_mode"])
    options.table_structure_options.do_cell_matching = config["do_cell_matching"]
    options.do_formula_enrichment = config["do_formula_enrichment"]
    return options


def preflight(config_path, single_input=None):
    configure_environment()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config["device"] != "cpu" or config["ocr_engine"] != "rapidocr":
        raise ValueError("本周入口仅支持 CPU + RapidOCR；修改实现前不静默切换引擎。")
    if config["num_threads"] < 1 or config["timeout_seconds_per_document"] <= 0:
        raise ValueError("线程数与单文档超时须为正数。")
    for name, expected in config["expected_packages"].items():
        if packages.version(name) != expected:
            raise ValueError(f"{name} 版本与配置不一致，请核对独立环境和锁定依赖。")
    manifest_path = repo_file(config["manifest"])
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if single_input:
        path = repo_file(str(single_input))
        manifest = {
            "schema_version": 1, "path_base": "repository_root",
            "documents": [{
                "id": "custom_pdf", "path": str(path.relative_to(REPO)),
                "sha256": digest(path),
                "source": "User-supplied local file; source/license/privacy not verified by program",
                "pages": "all", "page_count": None,
            }],
        }
    documents = manifest["documents"]
    if not documents or len({d["id"] for d in documents}) != len(documents):
        raise ValueError("输入清单为空或文档 ID 重复。")
    for doc in documents:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", doc["id"]):
            raise ValueError("文档 ID 仅能包含字母、数字、下划线与短横线。")
        path = repo_file(doc["path"])
        if path.suffix.lower() != ".pdf" or path.read_bytes()[:5] != b"%PDF-":
            raise ValueError(f"输入不是 PDF：{doc['id']}")
        if digest(path) != doc["sha256"]:
            raise ValueError(f"输入 SHA-256 不一致：{doc['id']}")
        if doc["pages"] != "all" and doc["pages"] != [1]:
            raise ValueError("本入口支持当前单页样例或新 PDF 的所有页面。")
    for reference in config["references"]:
        repo_file(reference).read_bytes()
    pipeline_options(config)  # Validate API/options without constructing a converter or loading models.
    return config, manifest, manifest_path


def worker(config_path, input_path, output_dir):
    """Each worker has its own process so a timeout/crash cannot stop the next PDF."""
    configure_environment()
    from docling.datamodel.base_models import ConversionStatus, InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption

    config = json.loads(config_path.read_text(encoding="utf-8"))
    tick = time.monotonic()
    converter = DocumentConverter(format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options(config))
    })
    result = converter.convert(input_path, raises_on_error=False)
    save_json(output_dir / "conversion-status.json", {
        "status": result.status.value, "elapsed_seconds_including_model_initialization": time.monotonic() - tick,
        "errors": [str(error) for error in result.errors],
    })
    # Preserve available output even on partial conversion; keep the non-success status.
    if result.document is not None:
        result.document.save_as_markdown(output_dir / "document.md")
        result.document.save_as_json(output_dir / "document.json")
    return 0 if result.status == ConversionStatus.SUCCESS else 1


def check_outputs(output_dir, expected_pages):
    checks = []
    markdown, structured = output_dir / "document.md", output_dir / "document.json"
    for path in [markdown, structured]:
        checks.append({"rule": f"{path.name} exists and is nonempty", "passed": path.is_file() and path.stat().st_size > 0})
    observations = {}
    try:
        from docling_core.types.doc import DoclingDocument
        data = json.loads(structured.read_text(encoding="utf-8"))
        document = DoclingDocument.model_validate(data)
        checks.append({"rule": "JSON validates as DoclingDocument", "passed": True})
        pages = len(document.pages)
        checks.append({"rule": "page count matches input" if expected_pages else "at least one page", "passed": pages == expected_pages if expected_pages else pages > 0})
        labels = [str(item.get("label", "")) for item in data.get("texts", [])]
        observations = {
            "page_count": pages, "text_element_count": len(labels),
            "heading_role_count": sum(label in ("title", "section_header") for label in labels),
            "table_count": len(data.get("tables", [])),
            "body_child_count": len(data.get("body", {}).get("children", [])),
            "note": "Counts only; title hierarchy, paragraphs, reading order and cells require user review.",
        }
    except Exception as error:
        checks.append({"rule": "JSON validates as DoclingDocument", "passed": False, "error": str(error)})
    return {"scope": "file/schema checks only; not a benchmark or semantic judgment", "checks": checks, "observations": observations, "passed": all(c["passed"] for c in checks)}


def git_text(*args):
    result = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, check=False)
    return result.stdout.strip()


def verify_model_files(config):
    report = json.loads((WEEK / "evidence/model-preparation.json").read_text(encoding="utf-8"))
    if not report["files"]:
        raise ValueError("模型准备记录为空。")
    revisions = {entry["repo_id"]: entry["resolved_revision"] for entry in report["sources"]}
    if revisions.get("docling-project/docling-layout-heron") != config["layout_revision"]:
        raise ValueError("版面模型准备记录与配置 revision 不一致。")
    for item in report["files"]:
        if digest(repo_file(item["path"])) != item["sha256"]:
            raise ValueError(f"模型文件哈希不一致：{item['path']}")


def run(config_path, prepared):
    config, manifest, manifest_path = prepared
    verify_model_files(config)
    stamp = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y%m%dT%H%M%S")
    run_dir = repo_file(config["output_root"]) / f"baseline-{stamp}-{uuid4().hex[:6]}"
    run_dir.mkdir(parents=True, exist_ok=False)
    snapshots = run_dir / "snapshots"
    snapshots.mkdir()
    snapshot_records = []
    sources = [config_path, manifest_path, Path(__file__), *(repo_file(p) for p in config["references"])]
    for source in sources:
        destination = snapshots / source.relative_to(REPO)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        snapshot_records.append({"source": str(source.relative_to(REPO)), "sha256": digest(source)})
    save_json(run_dir / "effective-input-manifest.json", manifest)
    with (WEEK / "reports/quality-review.csv").open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        selected_ids = {d["id"] for d in manifest["documents"]}
        with (run_dir / "review.csv").open("w", encoding="utf-8", newline="") as target:
            writer = csv.DictWriter(target, fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerows(row for row in reader if row["document_id"] in selected_ids)
    save_json(run_dir / "effective-pipeline-options.json", pipeline_options(config).model_dump(mode="json"))
    freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=True)
    (run_dir / "environment-freeze.txt").write_text(freeze.stdout, encoding="utf-8")
    metadata = {
        "status": "running", "started_at": now(), "timezone": "Asia/Shanghai",
        "command": [sys.executable, *sys.argv], "python": sys.version,
        "git_commit": git_text("rev-parse", "HEAD"), "git_status": git_text("status", "--porcelain").splitlines(),
        "config": config, "snapshots": snapshot_records, "documents": [],
        "evaluation": "pending_user_review; no semantic score",
        "timing_note": "Each PDF uses a fresh worker; elapsed includes model loading and any uncached downloads, not pure inference time.",
    }
    model_evidence = WEEK / "evidence/model-preparation.json"
    if model_evidence.exists():
        shutil.copyfile(model_evidence, run_dir / model_evidence.name)
        metadata["model_preparation_sha256"] = digest(model_evidence)
    meta_path = run_dir / "run-metadata.json"
    save_json(meta_path, metadata)
    print(f"输出目录：{run_dir}", flush=True)
    interrupted = False
    try:
        for doc in manifest["documents"]:
            folder = run_dir / doc["id"]
            folder.mkdir()
            command = [sys.executable, str(Path(__file__).resolve()), "--config", str(config_path), "--worker-input", str(repo_file(doc["path"])), "--worker-output", str(folder)]
            record = {"id": doc["id"], "input": doc["path"], "input_sha256": doc["sha256"], "started_at": now(), "command": command, "status": "running"}
            metadata["documents"].append(record)
            save_json(meta_path, metadata)
            tick = time.monotonic()
            with (folder / "stdout.log").open("wb") as stdout, (folder / "stderr.log").open("wb") as stderr:
                try:
                    # Check again at use time to avoid running changed input after preflight.
                    if digest(repo_file(doc["path"])) != doc["sha256"]:
                        raise ValueError("运行前输入哈希发生变化。")
                    result = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=config["timeout_seconds_per_document"], check=False)
                    record["exit_code"] = result.returncode
                except subprocess.TimeoutExpired:
                    record.update(exit_code=124, error="单份文档处理超时，子进程已结束。")
                except (OSError, ValueError) as error:
                    record.update(exit_code=1, error=str(error))
            record.update(finished_at=now(), elapsed_seconds=round(time.monotonic() - tick, 4))
            check = check_outputs(folder, doc.get("page_count"))
            save_json(folder / "mechanical-checks.json", check)
            record["status"] = "completed" if record["exit_code"] == 0 and check["passed"] else "failed"
            record["output_files"] = [{"file": str(p.relative_to(run_dir)), "sha256": digest(p), "bytes": p.stat().st_size} for p in sorted(folder.iterdir()) if p.is_file()]
            save_json(meta_path, metadata)
            print(f"{doc['id']}: {record['status']}, exit={record['exit_code']}, {record['elapsed_seconds']} 秒", flush=True)
    except KeyboardInterrupt:
        interrupted = True
        for record in metadata["documents"]:
            if record["status"] == "running":
                record.update(status="interrupted", finished_at=now(), exit_code=130)
    finally:
        metadata["status"] = "interrupted" if interrupted else ("completed" if len(metadata["documents"]) == len(manifest["documents"]) and all(d["status"] == "completed" for d in metadata["documents"]) else "failed")
        metadata["finished_at"] = now()
        save_json(meta_path, metadata)
    print("Markdown/JSON 为原始导出；机械检查不代表结构正确。review.csv 待本人核验。", flush=True)
    return 130 if interrupted else (0 if metadata["status"] == "completed" else 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=WEEK / "configs/baseline.json", help="解析配置，默认 CPU 基线")
    parser.add_argument("--prepare-only", action="store_true", help="只校验输入、依赖和选项；不构造解析器、不下载模型、不创建实验目录")
    parser.add_argument("--input", type=Path, help="可选：处理仓库内的一份新 PDF，来源与许可须另行记录；默认沿用三份固定输入")
    parser.add_argument("--worker-input", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--worker-output", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    config_path = args.config.resolve()
    try:
        if not config_path.is_relative_to(REPO):
            raise ValueError("配置文件必须在仓库内。")
        if args.worker_input:
            return worker(config_path, args.worker_input, args.worker_output)
        prepared = preflight(config_path, args.input)
        if args.prepare_only:
            print(f"准备检查通过：{len(prepared[1]['documents'])} 份 PDF；未下载模型或解析正文。")
            return 0
        return run(config_path, prepared)
    except Exception as error:
        parser.exit(2, f"准备或运行失败：{type(error).__name__}: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
