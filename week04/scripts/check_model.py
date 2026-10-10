import json
from datetime import datetime
from pathlib import Path

from huggingface_hub import HfApi

MODEL_ID = "Qwen/Qwen3.5-0.8B"

# 沿用 Week 2 记录的候选版本，先确认它可以访问。
REVISION = "2fc06364715b967f1860aea9cf38778875588b17"

root = Path(__file__).resolve().parent.parent
api = HfApi()

# 查询模型信息，不下载权重。
info = api.model_info(
    repo_id=MODEL_ID,
    revision=REVISION,
    timeout=30,
)

card = info.card_data
license_name = card.get("license") if card is not None else None

metadata = {
    "checked_at": datetime.now().astimezone().isoformat(),
    "model_id": MODEL_ID,
    "requested_revision": REVISION,
    "resolved_revision": info.sha,
    "license": license_name,
    "pipeline_tag": info.pipeline_tag,
    "planned_device": "cpu",
    "status": "metadata_access_verified; inference_not_run",
}

output = root / "configs" / "model-selection.json"
output.write_text(
    json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print(json.dumps(metadata, ensure_ascii=False, indent=2))
print(f"Saved: {output}")