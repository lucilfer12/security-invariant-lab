from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

class VerificationStatus(str, Enum):
    PROVEN = "PROVEN"
    VIOLATED = "VIOLATED"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True)
class VerificationResult:
    status: VerificationStatus
    model: dict[str, int] | None = None
    reason: str | None = None

class SMTUnavailable(RuntimeError):
    pass

def _solver():
    try:
        import z3
    except ImportError as exc:
        raise SMTUnavailable("Install security-invariant-lab[verification] for SMT support") from exc
    return z3.Solver(), z3

def prove(property_expr, constraints: Iterable = ()) -> VerificationResult:
    solver, z3 = _solver()
    for constraint in constraints:
        solver.add(constraint)
    solver.push()
    solver.add(z3.Not(property_expr))
    status = solver.check()
    if status == z3.unsat:
        solver.pop()
        return VerificationResult(VerificationStatus.PROVEN, reason="Negation of property is unsatisfiable.")
    if status == z3.sat:
        model = solver.model()
        values = {}
        for decl in model.decls():
            value = model.eval(decl(), model_completion=True)
            if z3.is_int_value(value):
                values[decl.name()] = value.as_long()
        solver.pop()
        return VerificationResult(VerificationStatus.VIOLATED, model=values, reason="Counterexample satisfies negated property.")
    solver.pop()
    return VerificationResult(VerificationStatus.UNKNOWN, reason="SMT solver returned unknown.")

def check_integer_property(property_builder, constraints=()):
    solver, z3 = _solver()
    symbols = {}
    for name in property_builder.symbols:
        symbols[name] = z3.Int(name)
    expr = property_builder.build(symbols)
    return prove(expr, constraints)
__all__ = ["VerificationStatus", "VerificationResult", "SMTUnavailable", "prove"]
