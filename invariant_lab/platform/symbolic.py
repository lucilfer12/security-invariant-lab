from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .smt import VerificationResult, prove

@dataclass(frozen=True)
class PathCondition:
    name: str
    assumptions: tuple[object, ...] = ()

    def add(self, *conditions: object) -> "PathCondition":
        return PathCondition(self.name, self.assumptions + tuple(conditions))

@dataclass
class SymbolicState:
    variables: dict[str, object] = field(default_factory=dict)
    paths: list[PathCondition] = field(default_factory=lambda: [PathCondition("entry")])

    def fork(self, condition: object, label: str) -> "SymbolicState":
        return SymbolicState(dict(self.variables), [
            p.add(condition) for p in self.paths
        ])

def verify_on_paths(property_expr, paths: Iterable[PathCondition]) -> list[VerificationResult]:
    results = []
    for path in paths:
        results.append(prove(property_expr, path.assumptions))
    return results

def summarize(results: Iterable[VerificationResult]) -> dict[str, int]:
    counts = {"PROVEN": 0, "VIOLATED": 0, "UNKNOWN": 0}
    for result in results:
        counts[result.status.value] += 1
    return counts

__all__ = ["PathCondition", "SymbolicState", "verify_on_paths", "summarize"]
