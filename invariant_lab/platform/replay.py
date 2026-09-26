from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"

def _git_commit(root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        return None

def create_bundle(root: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    root = Path(root).resolve()
    meta = {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "git_commit": _git_commit(root),
    }
    bundle = {"meta": meta, **payload}
    canonical = json.dumps(bundle, sort_keys=True, separators=(",", ":"))
    bundle["bundle_id"] = "RUN-" + hashlib.sha256(canonical.encode()).hexdigest()[:12].upper()
    return bundle

def write_bundle(root: str | Path, payload: dict[str, Any], path: str | Path | None = None) -> Path:
    root = Path(root).resolve()
    target = Path(path) if path else root / ".silab" / "runs" / "latest.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    bundle = create_bundle(root, payload)
    target.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target

def load_bundle(path: str | Path) -> dict[str, Any]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "meta" not in data or "bundle_id" not in data:
        raise ValueError("not a Security Invariant Lab replay bundle")
    return data

def redact_secret(value: str) -> str:
    if not value:
        return value
    if len(value) <= 8:
        return "***"
    return value[:4] + "…" + value[-4:]
