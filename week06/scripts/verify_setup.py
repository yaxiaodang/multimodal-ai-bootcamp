"""验证本机模型初始化；不调用 convert，不运行学习实验。"""

import importlib.metadata as packages
import json
import os
import platform
import sys
import time

from run_pipeline import WEEK, now, pipeline_options, preflight, save_json, verify_model_files


def main():
    config_path = WEEK / "configs/baseline.json"
    config, _, _ = preflight(config_path)
    verify_model_files(config)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption
    import torch

    started = now()
    tick = time.monotonic()
    converter = DocumentConverter(format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options(config))
    })
    converter.initialize_pipeline(InputFormat.PDF)
    report_path = WEEK / "evidence/model-preparation.json"
    report = json.loads(report_path.read_text())
    report.update(pipeline_initialized=True, initialization_checked_at=now(), initialization_elapsed_seconds=round(time.monotonic() - tick, 4), offline_initialization=True)
    save_json(report_path, report)
    save_json(WEEK / "evidence/environment.json", {
        "checked_at": now(), "started_at": started, "os": platform.freedesktop_os_release().get("PRETTY_NAME"),
        "python": sys.version, "executable": sys.executable,
        "packages": {name: packages.version(name) for name in ["pip", "docling", "docling-core", "docling-ibm-models", "docling-parse", "torch", "torchvision", "rapidocr", "onnxruntime", "transformers"]},
        "device": "cpu", "torch_cuda_available": torch.cuda.is_available(),
        "ocr_language": config["ocr_languages"], "ocr_version": "PP-OCRv6 (small detection/recognition; legacy angle classifier)",
        "models_initialized_offline": True, "learning_pdf_parsing_run": False,
        "quality_judgments": "pending_user_review",
    })
    print("本机 CPU 模型加载检查通过；未解析学习 PDF，未生成实验结果。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
