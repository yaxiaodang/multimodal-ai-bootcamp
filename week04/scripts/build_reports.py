"""刷新运行索引与完整 Prompt 清单；不覆盖人工评价或原始结果。"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
reports = ROOT / "reports"
lines = ["# 运行索引", "", "| 运行 | 预算/样例 | 记录状态 | 回答数 | 秒 | 证据 |", "| --- | --- | --- | --- | --- | --- |"]
for folder in sorted((ROOT / "runs").glob("paired-*")):
    m = json.loads((folder / "run-metadata.json").read_text())
    f = folder / "predictions.jsonl"
    n = len(f.read_text().splitlines()) if f.exists() else 0
    expected = len(m["samples"])*len(m["config"]["variants"])
    elapsed = f"{m['total_seconds']:.2f}" if "total_seconds" in m else "未记录"
    lines.append(f"| {folder.name} | {m['config']['max_new_tokens']} token / {len(m['samples'])} 图 | {m['status']} | {n}/{expected} | {elapsed} | [metadata](../runs/{folder.name}/run-metadata.json) |")
(reports / "runs.md").write_text("\n".join(lines)+"\n")
cfg = json.loads((ROOT / "configs/experiment-config-factors.json").read_text())
samples = json.loads((ROOT / "configs/sample-manifest.json").read_text())
lines = ["# 完整四组 Prompt", "", "每条文本同时输入对应图像，参考答案不传入模型。固定参数：", "```json", json.dumps({k:v for k,v in cfg.items() if k != "variants"},ensure_ascii=False,indent=2), "```"]
for s in samples:
    lines += ["", f"## {s['id']}", f"图像：`{s['image']}`"]
    for v, template in cfg["variants"].items():
        lines += ["", f"### {v}", "```text", template.format(question=s["question"]), "```"]
(reports / "prompts.md").write_text("\n".join(lines)+"\n")
print("Updated runs.md and prompts.md; reviews and raw results preserved.")
