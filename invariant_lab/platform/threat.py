from __future__ import annotations

from .types import ScanResult

def build_threat_model(result: ScanResult) -> dict:
    assets = sorted({v for c in result.contracts for v in c.state_variables})
    actors = [{"name": "ATTACKER", "capabilities": ["public/external entrypoints"]}]
    if any(f.modifiers for c in result.contracts for f in c.functions):
        actors.append({"name": "PRIVILEGED", "capabilities": ["modifier-gated entrypoints"]})
    trust_boundaries = []
    for c in result.contracts:
        if any(".call" in f.body for f in c.functions):
            trust_boundaries.append({"contract": c.name, "boundary": "external call"})
        if any(".delegatecall" in f.body for f in c.functions):
            trust_boundaries.append({"contract": c.name, "boundary": "delegatecall"})
    return {
        "assets": assets,
        "actors": actors,
        "trust_boundaries": trust_boundaries,
        "security_properties": [p.name for p in result.invariants],
        "assumptions": [
            "Analysis is local/static unless a runtime adapter is invoked.",
            "Heuristic findings require executable confirmation.",
        ],
    }
