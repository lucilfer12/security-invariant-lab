from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .engine import CaseResult


def build_evidence(results: Iterable[CaseResult]) -> dict:
    items = []
    for result in results:
        items.append(
            {
                "case": result.case.name,
                "passed": result.passed,
                "error": result.error,
                "finding": result.finding.to_dict() if result.finding else None,
            }
        )
    return {"version": 1, "results": items}


def write_evidence(results: Iterable[CaseResult], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(build_evidence(results), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target
