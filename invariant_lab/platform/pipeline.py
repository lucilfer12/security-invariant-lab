from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from .graphs import attack_paths, build_graph, to_dot
from .invariants import discover_invariants, property_statuses
from .mutation import suggest_mutations
from .replay import write_bundle
from .report import write_reports
from .scanner import SolidityScanner, attack_surface
from .types import ScanResult

def _tool_version(command: str) -> str | None:
    try:
        out = subprocess.check_output([command, "--version"], text=True, stderr=subprocess.STDOUT, timeout=8)
        return out.splitlines()[0].strip()
    except Exception:
        return None

def scan_project(root: str | Path, out_dir: str | Path = ".silab") -> tuple[ScanResult, Path]:
    root = Path(root).resolve()
    out = Path(out_dir)
    scanner = SolidityScanner(root)
    result = scanner.scan()
    result.invariants.extend(discover_invariants(result))
    graph = build_graph(result)
    paths = attack_paths(graph)
    result.metrics.update({
        "candidate_invariants": len(result.invariants),
        "attack_graph_nodes": len(graph.nodes),
        "attack_graph_edges": len(graph.edges),
        "candidate_attack_paths": len(paths),
        "forge_available": bool(_tool_version("forge")),
        "anvil_available": bool(_tool_version("anvil")),
    })
    out.mkdir(parents=True, exist_ok=True)
    scan_path = out / "scan.json"
    scan_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "attack-surface.json").write_text(json.dumps(attack_surface(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "properties.json").write_text(json.dumps(property_statuses(result.invariants), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "graph.dot").write_text(to_dot(graph), encoding="utf-8")

    mutation_count = 0
    for contract in result.contracts:
        mutation_count += len(suggest_mutations(contract.file))
    result.metrics["mutation_candidates"] = mutation_count

    write_reports(result, out)
    bundle = write_bundle(root, {
        "kind": "scan",
        "target": str(root),
        "metrics": result.metrics,
        "properties": property_statuses(result.invariants),
        "attack_paths": paths,
        "finding_ids": [f.id for f in result.findings],
    }, out / "runs" / "latest.json")
    result.metrics["bundle_id"] = bundle["bundle_id"]
    scan_path.write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result, out

def forge_test(target: str | Path) -> dict[str, Any]:
    target = Path(target).resolve()
    version = _tool_version("forge")
    if not version:
        return {"available": False, "command": "forge", "error": "Forge is not installed or not on PATH."}
    try:
        proc = subprocess.run(
            ["forge", "test", "-vv"],
            cwd=target,
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
        )
        return {
            "available": True,
            "version": version,
            "returncode": proc.returncode,
            "stdout": proc.stdout[-12000:],
            "stderr": proc.stderr[-6000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {"available": True, "version": version, "error": "forge test timed out", "stdout": (exc.stdout or "")[-6000:]}
__all__ = ["scan_project", "forge_test"]
