"""按已核对的固定四组运行整理评价；不是通用自动评分器。"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / "runs" / "paired-20261010T152113-073899"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
target = REPORTS / "review.csv"
if target.exists():
    raise FileExistsError("review-factors.csv 已存在；保留现有评价，不自动覆盖")

manifest = json.loads((ROOT / "configs" / "sample-manifest.json").read_text())
# 标签来自逐项证据核对，固定在本次历史输出，不根据关键词猜测新输出。
overrides = {
    ("count", "S"): ("incorrect", "not_applicable", "counting", "实际 7，答 9"),
    ("count", "E"): ("correct", "incorrect", "counting/reasoning", "最终答 7，但中排误数 2，且 3+2+1 不等于 7"),
    ("chart", "E"): ("incorrect", "not_applicable", "visual_comparison/reasoning", "实际 B 最高，答 C"),
    ("arithmetic", "E"): ("incorrect", "not_applicable", "reasoning", "正确总价 10，答 7；错误机制未知"),
    ("arithmetic", "S"): ("incorrect", "not_applicable", "reasoning", "正确总价 10，答 7；错误机制未知"),
    ("arithmetic", "B"): ("incorrect", "not_applicable", "reasoning", "正确总价 10，答 7；错误机制未知"),
    ("occluded", "A"): ("unanswered", "not_applicable", "task_completion", "空回答，未达到上限"),
    ("occluded", "E"): ("correct", "mixed", "unsupported_description", "拒绝确认编号正确，但遮挡不能证明框下内容为空"),
    ("occluded", "S"): ("incorrect", "not_applicable", "hallucination", "编造 123456，无可见证据"),
    ("occluded", "B"): ("incorrect", "not_applicable", "hallucination", "回答 0，无可见证据"),
}
has_explanation = {("chart", "A"), ("arithmetic", "A"), ("missing_date", "A")}
rows = []
for sample in manifest:
    for variant in ["A", "E", "S", "B"]:
        source = RUN / "predictions.jsonl"
        record = next(json.loads(line) for line in source.read_text().splitlines() if (json.loads(line)["sample_id"], json.loads(line)["variant"]) == (sample["id"], variant))
        default = ("correct", "supported" if (sample["id"], variant) in has_explanation else "not_applicable", "", "满足任务答案；等价表达可接受")
        task, explanation, category, notes = overrides.get((sample["id"], variant), default)
        if sample["id"] == "shapes":
            task, explanation, category, notes = "partial", "not_applicable", "shape/spatial", "矩形误称 square，未明确左右对应关系"
        rows.append({"sample_id": sample["id"], "variant": variant,
                     "task_correctness": task, "explanation_faithfulness": explanation,
                     "error_category": category, "notes": notes,
                     "reviewer": "Codex evidence review; user confirmed rubric and five key references",
                     "user_review": "", "user_notes": "", "answer": record["answer"],
                     "reference_answer": record["reference_answer"], "prompt": record["prompt"],
                     "generated_tokens": record["generated_tokens"], "token_limit_reached": record["token_limit_reached"],
                     "evidence": str(source.relative_to(ROOT))})
with target.open("w", newline="", encoding="utf-8") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)

summary = {v: dict(Counter(r["task_correctness"] for r in rows if r["variant"] == v)) for v in ["A", "E", "S", "B"]}
(REPORTS / "metrics.json").write_text(json.dumps({
    "run": RUN.name, "scope": "10 fixed teaching images; not population accuracy",
    "rubric": "task correctness and explanation faithfulness separately",
    "task_counts": summary, "explanation_issues": [f"{r['sample_id']}/{r['variant']}" for r in rows if r["explanation_faithfulness"] in ["incorrect", "mixed"]],
    "review_provenance": "Codex evidence review under user-confirmed rubric; not user approval of every row",
}, ensure_ascii=False, indent=2)+"\n")
print("Saved review-factors.csv and metrics-factors.json; raw outputs unchanged.")
