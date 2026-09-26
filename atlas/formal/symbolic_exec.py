from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable
from .smt import SMTContext, ModelResult

@dataclass
class Path:
    conditions: list[object] = field(default_factory=list)
    trace: list[str] = field(default_factory=list)

class SymbolicExecutor:
    """Path-sensitive arithmetic executor backed by Z3 for bounded assertions."""
    def __init__(self):
        self.ctx = SMTContext()

    def symbol(self, name: str):
        return self.ctx.int(name)

    def branch(self, path: Path, condition, label: str) -> tuple[Path, Path]:
        taken = Path(path.conditions + [condition], path.trace + [label + ":true"])
        other = Path(path.conditions + [~condition], path.trace + [label + ":false"])
        return taken, other

    def feasible(self, path: Path) -> ModelResult:
        self.ctx.solver.push()
        try:
            self.ctx.add(*path.conditions)
            return self.ctx.check()
        finally:
            self.ctx.solver.pop()

    def find_assertion_violation(self, path: Path, assertion, label: str) -> ModelResult:
        self.ctx.solver.push()
        try:
            self.ctx.add(*path.conditions)
            self.ctx.add(~assertion)
            result = self.ctx.check()
            if result.status == "sat":
                return ModelResult("sat", result.model, label + " violated")
            return result
        finally:
            self.ctx.solver.pop()

    def explore(self, initial: Path, steps: list[Callable[[Path], tuple[Path, Path]]]) -> list[Path]:
        paths = [initial]
        for step in steps:
            next_paths = []
            for path in paths:
                next_paths.extend(step(path))
            paths = [p for p in next_paths if self.feasible(p).status == "sat"]
        return paths
