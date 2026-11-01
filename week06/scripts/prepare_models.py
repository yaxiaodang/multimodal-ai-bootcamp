"""准备模型文件并记录来源/哈希；不读取或解析学习 PDF。"""

import argparse
import hashlib
import json
import os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[2]
WEEK = REPO / "week06"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hf-only", action="store_true", help="只准备版面和表格模型，OCR 依赖安装后再运行完整准备")
    args = parser.parse_args()
    os.environ["HF_HOME"] = str(REPO / ".cache-week06/huggingface")
    os.environ["DOCLING_CACHE_DIR"] = str(REPO / ".cache-week06/docling")
    os.environ["HF_HUB_DISABLE_XET"] = "1"
    from huggingface_hub import snapshot_download

    config = json.loads((WEEK / "configs/baseline.json").read_text())
    artifacts = REPO / config["artifacts_path"]
    sources = json.loads((WEEK / "evidence/model-sources.json").read_text())
    # Inspect model cards before fetching weights. Pin remote revisions in source evidence.
    for source in sources:
        target = artifacts / source["repo_id"].replace("/", "--")
        snapshot_download(source["repo_id"], revision=source["resolved_revision"], local_dir=target,
                          allow_patterns=["README.md"], token=False)
        print(f"Model card: {source['model_card_url']}; license: {source['license']}", flush=True)
        print((target / "README.md").read_text()[:3800], flush=True)
    for source in sources:
        target = artifacts / source["repo_id"].replace("/", "--")
        patterns = ["config.json", "preprocessor_config.json", "model.safetensors", "README.md", "LICENSE*"]
        if source["repo_id"].endswith("docling-models"):
            patterns = ["model_artifacts/tableformer/accurate/*", "README.md", "LICENSE*"]
        snapshot_download(source["repo_id"], revision=source["resolved_revision"], local_dir=target,
                          allow_patterns=patterns, token=False, max_workers=2)
        print(f"Prepared: {source['repo_id']} @ {source['resolved_revision']}", flush=True)
    if args.hf_only:
        return 0

    from docling.models.stages.ocr.rapid_ocr_model import RapidOcrModel
    RapidOcrModel.download_models(backend=config["ocr_backend"], local_dir=artifacts / "RapidOcr",
                                 lang=config["ocr_languages"][0], progress=True)
    files = []
    for path in sorted(artifacts.rglob("*")):
        if path.is_file() and ".cache" not in path.relative_to(artifacts).parts:
            files.append({"path": str(path.relative_to(REPO)), "bytes": path.stat().st_size,
                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    report = {
        "checked_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "scope": "model_files_only_no_pdf_parsing", "sources": sources,
        "ocr": {"engine": "RapidOCR", "backend": config["ocr_backend"], "language": config["ocr_languages"],
                "source": "Docling 2.145.0 RapidOcrModel.download_models + RapidOCR registry",
                "note": "OCR artifact URLs are recorded in the preparation log and OCR source evidence."},
        "files": files, "pipeline_initialized": False, "pdf_parsing_run": False,
    }
    (WEEK / "evidence/model-preparation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"Recorded hashes for {len(files)} local artifacts; no PDF parsed.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
