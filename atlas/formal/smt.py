from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

try:
    import z3
except ImportError as exc:  # pragma: no cover
    z3 = None
    _Z3_ERROR = exc
else:
    _Z3_ERROR = None

class SMTUnavailable(RuntimeError):
    pass

@dataclass(frozen=True)
class ModelResult:
    status: str
    model: dict[str, int]
    reason: str = ""

class SMTContext:
    """Thin, deterministic Z3 facade for bounded arithmetic/protocol properties."""
    def __init__(self):
        if z3 is None:
            raise SMTUnavailable("install z3-solver to use SMTContext") from _Z3_ERROR
        self.solver = z3.Solver()
        self._ints: dict[str, object] = {}

    def int(self, name: str):
        if not name:
            raise ValueError("symbol name cannot be empty")
        self._ints.setdefault(name, z3.Int(name))
        return self._ints[name]

    def add(self, *constraints) -> None:
        self.solver.add(*constraints)

    def assume_range(self, symbol, lo: int, hi: int) -> None:
        if lo > hi:
            raise ValueError("invalid range")
        self.add(symbol >= lo, symbol <= hi)

    def check(self, target=None) -> ModelResult:
        if target is not None:
            self.solver.push()
            self.solver.add(target)
        try:
            status = self.solver.check()
            if status == z3.sat:
                model = self.solver.model()
                values = {name: model.eval(sym, model_completion=True).as_long()
                          for name, sym in self._ints.items()}
                return ModelResult("sat", values)
            if status == z3.unsat:
                return ModelResult("unsat", {})
            return ModelResult("unknown", {}, str(status))
        finally:
            if target is not None:
                self.solver.pop()

    def prove(self, assertion) -> ModelResult:
        return self.check(z3.Not(assertion))


def prove_bounded(
    variables: Iterable[tuple[str, int, int]],
    assumptions: Iterable[Callable[[SMTContext], object]],
    property_builder: Callable[[SMTContext], object],
) -> ModelResult:
    ctx = SMTContext()
    for name, lo, hi in variables:
        ctx.assume_range(ctx.int(name), lo, hi)
    for assumption in assumptions:
        ctx.add(assumption(ctx))
    return ctx.prove(property_builder(ctx))
