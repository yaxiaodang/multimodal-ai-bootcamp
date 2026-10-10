"""核对每轮 JSONL 记录、输入哈希和完整 Prompt；未完成运行单独报告。"""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
count = 0
for folder in sorted((ROOT / "runs").glob("paired-*")):
    meta = json.loads((folder / "run-metadata.json").read_text())
    predictions = folder / "predictions.jsonl"
    records = [json.loads(line) for line in predictions.read_text().splitlines()] if predictions.exists() else []
    expected = {(s["id"], v) for s in meta["samples"] for v in meta["config"]["variants"]}
    actual = {(r["sample_id"], r["variant"]) for r in records}
    assert len(actual) == len(records), "重复记录"
    assert actual <= expected, "未知样例或组"
    if meta["status"] == "completed":
        assert actual == expected, f"完整运行缺少回答：{folder.name}"
    for r in records:
        s = next(s for s in meta["samples"] if s["id"] == r["sample_id"])
        assert r["input_sha256"] == hashlib.sha256((ROOT / s["image"]).read_bytes()).hexdigest(), "输入哈希不一致"
        assert r["prompt"] == meta["config"]["variants"][r["variant"]].format(question=s["question"]), "Prompt 不一致"
        assert r["generated_tokens"] <= meta["config"]["max_new_tokens"], "长度不一致"
    count += len(records)
    print(f"{folder.name}: {len(records)}/{len(expected)} records; recorded status={meta['status']}")
print(f"Verified {count} saved predictions. Evidence consistency is not fresh-environment reproducibility.")
