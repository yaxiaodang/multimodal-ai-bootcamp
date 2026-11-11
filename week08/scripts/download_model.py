"""Download only the pinned public model assets needed by Week08."""
import json
from pathlib import Path
from huggingface_hub import snapshot_download

root = Path(__file__).resolve().parents[2]
cfg = json.loads((root / 'week08/configs/run-a.json').read_text())
print(snapshot_download(cfg['model_id'], revision=cfg['revision'], cache_dir=str(root/cfg['cache_dir']),
                        allow_patterns=['*.json','*.safetensors','*.txt','*.md','LICENSE*']))
