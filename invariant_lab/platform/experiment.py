from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .pipeline import forge_test, scan_project
from .replay import write_bundle

@dataclass(frozen=True)
class ExperimentSpec:
    name: str
    target: str
    strategies: tuple[str, ...] = ("scan",)
    repeats: int = 1

def load_spec(path: str | Path) -> ExperimentSpec:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return ExperimentSpec(data["name"], data["target"], tuple(data.get("strategies", ("scan",))), int(data.get("repeats", 1)))

def run(spec: ExperimentSpec, out_dir: str | Path) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for index in range(spec.repeats):
        entry = {"iteration": index, "started_at": datetime.now(timezone.utc).isoformat()}
        if "scan" in spec.strategies:
            scan, _ = scan_project(spec.target, out / ("scan-{:03d}".format(index)))
            entry["scan"] = scan.metrics
        if "forge-test" in spec.strategies:
            entry["forge_test"] = forge_test(spec.target)
        results.append(entry)
    payload = {"name": spec.name, "target": spec.target, "strategies": list(spec.strategies), "results": results}
    write_bundle(spec.target, {"kind": "experiment", **payload}, out / "experiment-run.json")
    (out / "experiment.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
