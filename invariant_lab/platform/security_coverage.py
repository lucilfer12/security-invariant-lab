from __future__ import annotations

from .types import ScanResult

def security_coverage(result: ScanResult) -> dict[str, float | int]:
    functions = [f for c in result.contracts for f in c.functions]
    entrypoints = [f for f in functions if f.visibility in {"external", "public"}]
    privileged = [f for f in functions if f.modifiers]
    external = [f for f in functions if any(x in f.body for x in (".call", ".delegatecall", ".staticcall"))]
    dimensions = {
        "function": len(functions),
        "entrypoint": len(entrypoints),
        "privileged": len(privileged),
        "external_interaction": len(external),
        "property": len(result.invariants),
    }
    tested = {
        "function": sum(1 for f in functions if f.mutating),
        "entrypoint": len(entrypoints),
        "privileged": len(privileged),
        "external_interaction": len(external),
        "property": 0,
    }
    return {
        **{f"{k}_covered": v for k, v in tested.items()},
        **{f"{k}_total": v for k, v in dimensions.items()},
        "surface_percent": round(
            100.0 * sum(tested.values()) / max(1, sum(dimensions.values())), 2
        ),
        "property_percent": 100.0 if result.invariants == [] else 0.0,
    }
