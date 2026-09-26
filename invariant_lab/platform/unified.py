from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ai import ai_report
from .capabilities import manifest
from .pipeline import forge_test, scan_project

def unified_manifest() -> dict[str, Any]:
    data = manifest()
    try:
        from atlas.manifest import default_manifest
        atlas = default_manifest()
        data["atlas"] = {
            "name": atlas.name,
            "version": atlas.version,
            "capabilities": list(atlas.capabilities),
        }
    except Exception as exc:
        data["atlas"] = {"available": False, "error": type(exc).__name__}
    data["architecture"] = {
        "core": "invariant execution",
        "intelligence": "source/graph/threat/taint analysis",
        "verification": "executable properties + optional SMT",
        "runtime": "authorized Foundry/Anvil adapters",
        "evidence": "replayable machine-readable bundles",
        "copilot": "optional Gemini hypothesis layer",
    }
    return data

def analyze_project(root: str | Path, out_dir: str | Path = ".silab") -> dict:
    result, out = scan_project(root, out_dir)
    return {
        "metrics": result.metrics,
        "findings": [f.__dict__ for f in result.findings],
        "properties": [p.__dict__ for p in result.invariants],
        "forge": forge_test(root) if (Path(root) / "foundry.toml").exists() else {"available": False},
        "ai": ai_report(result.to_dict()),
        "out": str(out.resolve()),
    }

def write_unified_manifest(path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(unified_manifest(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target

__all__ = ["unified_manifest", "analyze_project", "write_unified_manifest"]
