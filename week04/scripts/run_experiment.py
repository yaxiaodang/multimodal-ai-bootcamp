"""固定样例的配对 Prompt 对照；模型加载一次，人工评价另行填写。"""
import argparse
import csv
import hashlib
import json
import platform
import subprocess
import time
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
import torch
from PIL import Image
from transformers import AutoProcessor, Qwen3_5ForConditionalGeneration

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", help="只运行某个样例 ID；省略则运行全部十张")
    parser.add_argument("--prepare-only", action="store_true", help="离线验证全部输入，不加载模型权重")
    parser.add_argument("--config", default="experiment-config.json", help="相对于 week04 的配置路径，默认原始 32 token 配置")
    args = parser.parse_args()
    samples = json.loads((ROOT / "configs" / "sample-manifest.json").read_text())
    if args.sample:
        samples = [s for s in samples if s["id"] == args.sample]
        if not samples:
            parser.error("未知样例 ID")
    cfg = json.loads((ROOT / "configs" / args.config).read_text())
    sel = json.loads((ROOT / "configs" / "model-selection.json").read_text())
    torch.set_num_threads(cfg["cpu_threads"])
    torch.manual_seed(cfg["seed"])
    processor = AutoProcessor.from_pretrained(sel["model_id"], revision=sel["resolved_revision"], local_files_only=True)

    def prepare(sample, variant):
        prompt = cfg["variants"][variant].format(question=sample["question"])
        with Image.open(ROOT / sample["image"]) as source:
            image = source.convert("RGB")
        messages = [{"role": "user", "content": [{"type": "image", "image": image}, {"type": "text", "text": prompt}]}]
        inputs = processor.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=True, return_tensors="pt", enable_thinking=cfg["enable_thinking"])
        return prompt, inputs

    if args.prepare_only:
        for s in samples:
            for v in cfg["variants"]:
                _, inputs = prepare(s, v)
                print(s["id"], v, "tokens:", inputs["input_ids"].shape[-1], "pixels:", tuple(inputs["pixel_values"].shape))
        print("Input validation OK; no model inference performed.")
        return

    out = ROOT / "runs" / datetime.now().astimezone().strftime("paired-%Y%m%dT%H%M%S-%f")
    out.mkdir(parents=True)
    metadata = {"started_at": datetime.now().astimezone().isoformat(), "status": "loading", "model": sel, "config_file": args.config, "config": cfg, "samples": samples,
                "python": platform.python_version(), "packages": {p: version(p) for p in ["torch", "torchvision", "transformers", "Pillow", "huggingface-hub"]},
                "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "git_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
                "comparison": "A/B paired by sample; fixed A then B order; elapsed times are not a rigorous speed benchmark"}
    def save():
        (out / "run-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+"\n")
    save()
    print(f"Run directory: {out}", flush=True)
    start = time.perf_counter()
    try:
        model = Qwen3_5ForConditionalGeneration.from_pretrained(sel["model_id"], revision=sel["resolved_revision"], local_files_only=True, dtype=torch.float32, attn_implementation=cfg["attention"]).to("cpu").eval()
        metadata["load_seconds"] = time.perf_counter()-start
        metadata["status"] = "running"
        save()
        with (out / "review.csv").open("w", newline="", encoding="utf-8") as review:
            fields = ["sample_id", "variant", "answer", "reference_answer", "verdict", "error_category", "notes", "evidence"]
            writer = csv.DictWriter(review, fieldnames=fields)
            writer.writeheader()
            for s in samples:
                for v in cfg["variants"]:
                    print(f"Running {s['id']} / {v}", flush=True)
                    prompt, inputs = prepare(s, v)
                    print(f"Full prompt [{v}]: {prompt}", flush=True)
                    t = time.perf_counter()
                    with torch.inference_mode():
                        result = model.generate(**inputs, do_sample=cfg["do_sample"], max_new_tokens=cfg["max_new_tokens"])
                    tokens = result[0, inputs["input_ids"].shape[-1]:]
                    answer = processor.decode(tokens, skip_special_tokens=True)
                    row = {"sample_id": s["id"], "variant": v, "prompt": prompt, "answer": answer, "reference_answer": s["reference_answer"], "criteria": s["criteria"],
                           "input_sha256": hashlib.sha256((ROOT / s["image"]).read_bytes()).hexdigest(), "input_tokens": inputs["input_ids"].shape[-1],
                           "generated_tokens": len(tokens), "token_limit_reached": len(tokens) >= cfg["max_new_tokens"], "generation_seconds": time.perf_counter()-t}
                    with (out / "predictions.jsonl").open("a", encoding="utf-8") as predictions:
                        predictions.write(json.dumps(row, ensure_ascii=False)+"\n")
                    writer.writerow({"sample_id": s["id"], "variant": v, "answer": answer, "reference_answer": s["reference_answer"], "evidence": f"predictions.jsonl ({s['id']}/{v})"})
                    review.flush()
                    print(f"Answer: {answer}", flush=True)
        metadata["status"] = "completed"
    except Exception as exc:
        metadata.update(status="failed", error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        metadata["total_seconds"] = time.perf_counter()-start
        save()


if __name__ == "__main__":
    main()
