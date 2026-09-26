from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .detectors import builtin_registry
from .export import write_exports
from .graphs import attack_paths, build_graph, to_dot
from .invariants import discover_invariants, property_statuses
from .mutation import suggest_mutations
from .replay import write_bundle
from .report import write_reports
from .rootcause import root_cause_candidates
from .scanner import SolidityScanner, attack_surface
from .security_coverage import security_coverage
from .taint import taint_report
from .threat import build_threat_model
from .types import ScanResult
from protocols.packs import load_default_registry

def _tool_path(command: str) -> str | None:
    env = os.getenv("SILAB_" + command.upper() + "_BIN")
    if env and Path(env).exists():
        return env
    found = shutil.which(command)
    if found:
        return found
    candidate = Path.home() / "Tools" / "foundry" / (command + ".exe")
    return str(candidate) if candidate.exists() else None
def _tool_version(command: str) -> str | None:
    path = _tool_path(command)
    if not path:
        return None
    try:
        out = subprocess.check_output([path, "--version"], text=True, stderr=subprocess.STDOUT, timeout=8)
        return out.splitlines()[0].strip()
    except Exception:
        return None

def scan_project(root: str | Path, out_dir: str | Path = ".silab") -> tuple[ScanResult, Path]:
    root = Path(root).resolve()
    out = Path(out_dir)
    result = SolidityScanner(root).scan()
    result.invariants.extend(discover_invariants(result))
    registry = builtin_registry()
    result.findings.extend(registry.run_all(result))
    graph = build_graph(result)
    paths = attack_paths(graph)
    coverage = security_coverage(result)
    threat = build_threat_model(result)
    taint = taint_report(result)
    root_causes = root_cause_candidates(result)
    pack_registry = load_default_registry()
    identifiers = {
        token
        for contract in result.contracts
        for token in list(contract.state_variables) + [f.name for f in contract.functions]
    }
    matched_packs = pack_registry.match(identifiers)
    result.metrics.update({
        "candidate_invariants": len(result.invariants),
        "attack_graph_nodes": len(graph.nodes),
        "attack_graph_edges": len(graph.edges),
        "candidate_attack_paths": len(paths),
        "forge_available": bool(_tool_version("forge")),
        "anvil_available": bool(_tool_version("anvil")),
        "taint_paths": len(taint),
        "surface_percent": coverage["surface_percent"],
        "property_percent": coverage["property_percent"],
        "detector_count": len(registry.all()),
        "root_cause_hypotheses": len(root_causes),
        "matched_protocol_packs": len(matched_packs),
    })
    out.mkdir(parents=True, exist_ok=True)
    (out / "scan.json").write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (out / "security-coverage.json").write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
    (out / "threat-model.json").write_text(json.dumps(threat, indent=2) + "\n", encoding="utf-8")
    (out / "taint.json").write_text(json.dumps(taint, indent=2) + "\n", encoding="utf-8")
    (out / "root-cause.json").write_text(json.dumps(root_causes, indent=2) + "\n", encoding="utf-8")
    (out / "attack-surface.json").write_text(json.dumps(attack_surface(result), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "properties.json").write_text(json.dumps(property_statuses(result.invariants), indent=2) + "\n", encoding="utf-8")
    (out / "graph.dot").write_text(to_dot(graph), encoding="utf-8")
    mutation_count = sum(len(suggest_mutations(c.file)) for c in result.contracts)
    result.metrics["mutation_candidates"] = mutation_count
    payload = {
        "kind": "scan",
        "target": str(root),
        "metrics": result.metrics,
        "properties": property_statuses(result.invariants),
        "attack_paths": paths,
        "finding_ids": [f.id for f in result.findings],
    }
    bundle_path = write_bundle(root, payload, out / "runs" / "latest.json")
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    result.metrics["bundle_id"] = bundle["bundle_id"]
    exports = write_exports(result, out)
    result.metrics["export_artifacts"] = sorted(exports)
    write_reports(result, out)
    (out / "scan.json").write_text(
        json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result, out

def forge_test(target: str | Path) -> dict[str, Any]:
    target = Path(target).resolve()
    forge = _tool_path("forge")
    if not forge:
        return {"available": False, "command": "forge", "error": "Forge is not installed or not discoverable."}
    command = [forge, "test", "-vvv"]
    try:
        proc = subprocess.run(command, cwd=target, text=True, capture_output=True, timeout=300, check=False)
        return {
            "available": True,
            "version": _tool_version("forge"),
            "returncode": proc.returncode,
            "stdout": proc.stdout[-12000:],
            "stderr": proc.stderr[-6000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "available": True, "version": _tool_version("forge"), "returncode": None,
            "stdout": (exc.stdout or "")[-6000:], "stderr": "forge test timed out",
        }

__all__ = ["scan_project", "forge_test"]
