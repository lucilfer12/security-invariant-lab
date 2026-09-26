from __future__ import annotations

import json
from pathlib import Path

def load_scan(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def compare_scans(baseline: dict, current: dict) -> dict:
    old = {f["id"]: f for f in baseline.get("findings", [])}
    new = {f["id"]: f for f in current.get("findings", [])}
    return {
        "introduced": sorted(set(new) - set(old)),
        "resolved": sorted(set(old) - set(new)),
        "unchanged": sorted(set(old) & set(new)),
        "baseline_root": baseline.get("root"),
        "current_root": current.get("root"),
    }
