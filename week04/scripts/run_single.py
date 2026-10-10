"""CPU 单图试运行：固定版本，保存原始答案、配置与运行状态。"""
import hashlib
import json
import platform
import sys
import time
from datetime import datetime
from importlib.metadata import version
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen3_5ForConditionalGeneration

ROOT = Path(__file__).resolve().parent.parent


def main():
    selection = json.loads((ROOT / "configs" / "model-selection.json").read_text())
    config = json.loads((ROOT / "configs" / "single-config.json").read_text())
    image_path = ROOT / config["image"]
    if not image_path.is_file():
        raise FileNotFoundError("请先运行 week04/scripts/prepare_samples.py 生成图片")

    run_id = datetime.now().astimezone().strftime("single-%Y%m%dT%H%M%S-%f")
    output_dir = ROOT / "runs" / run_id
    output_dir.mkdir(parents=True)
    record = {
        "run_id": run_id,
        "started_at": datetime.now().astimezone().isoformat(),
        "status": "started",
        "model_id": selection["model_id"],
        "revision": selection["resolved_revision"],
        "config": config,
        "input_sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
        "python": platform.python_version(),
        "packages": {p: version(p) for p in ["torch", "transformers", "Pillow", "huggingface-hub"]},
        "manual_review": "pending",
    }
    result_path = output_dir / "result.json"

    def save():
        result_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")

    save()
    print(f"Run directory: {output_dir}", flush=True)
    torch.set_num_threads(config["cpu_threads"])
    torch.manual_seed(config["seed"])
    start = time.perf_counter()
    try:
        print("[1/3] Loading processor and model (first run downloads weights)...", flush=True)
        processor = AutoProcessor.from_pretrained(record["model_id"], revision=record["revision"])
        model = Qwen3_5ForConditionalGeneration.from_pretrained(
            record["model_id"], revision=record["revision"],
            dtype=torch.float32, attn_implementation="sdpa",
        ).to("cpu").eval()
        record["load_seconds"] = time.perf_counter() - start
        save()
        print("[2/3] Preparing image and question...", flush=True)
        with Image.open(image_path) as source:
            image = source.convert("RGB")
        messages = [{"role": "user", "content": [
            {"type": "image", "image": image},
            {"type": "text", "text": config["prompt"]},
        ]}]
        inputs = processor.apply_chat_template(
            messages, tokenize=True, add_generation_prompt=True,
            return_dict=True, return_tensors="pt", enable_thinking=False,
        ).to("cpu")
        record["input_tokens"] = inputs["input_ids"].shape[-1]
        print("[3/3] Generating answer on CPU...", flush=True)
        generation_start = time.perf_counter()
        with torch.inference_mode():
            outputs = model.generate(
                **inputs, max_new_tokens=config["max_new_tokens"],
                do_sample=config["do_sample"],
            )
        generated = outputs[0, inputs["input_ids"].shape[-1]:]
        answer = processor.decode(generated, skip_special_tokens=True)
        (output_dir / "answer.txt").write_text(answer + "\n", encoding="utf-8")
        record.update({
            "status": "completed", "answer": answer,
            "generation_seconds": time.perf_counter() - generation_start,
            "generated_tokens": len(generated),
            "token_limit_reached": len(generated) >= config["max_new_tokens"],
        })
        print(f"Answer: {answer}", flush=True)
    except Exception as exc:
        record.update({"status": "failed", "error_type": type(exc).__name__, "error": str(exc)})
        raise
    finally:
        record["total_seconds"] = time.perf_counter() - start
        save()
        print(f"Saved: {result_path}", flush=True)


if __name__ == "__main__":
    main()
