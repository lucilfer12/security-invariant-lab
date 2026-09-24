from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Protocol

from .invariants import Invariant
from .model import Event, Finding, StateSnapshot


class Model(Protocol):
    def fresh(self) -> Any: ...
    def apply(self, state: Any, event: Event) -> None: ...
    def snapshot(self, state: Any, label: str = "state") -> StateSnapshot: ...


@dataclass(frozen=True)
class Case:
    name: str
    events: tuple[Event, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CaseResult:
    case: Case
    passed: bool
    finding: Finding | None = None
    error: str | None = None


class Engine:
    def __init__(self, model: Model, invariants: Iterable[Invariant]):
        self.model = model
        self.invariants = tuple(invariants)

    def run_case(self, case: Case, *, stop_on_failure: bool = True) -> CaseResult:
        state = self.model.fresh()
        previous = self.model.snapshot(state, "initial")
        trace: list[Event] = []

        for event in case.events:
            trace.append(event)
            self.model.apply(state, event)
            current = self.model.snapshot(state, f"after:{event.name}")
            for invariant in self.invariants:
                try:
                    result = invariant.check(state)
                except Exception as exc:  # invariant exceptions are findings about the harness/model
                    finding = Finding(
                        invariant=invariant.name,
                        message=f"Invariant execution raised {type(exc).__name__}: {exc}",
                        trace=tuple(trace),
                        before=previous,
                        after=current,
                        metadata={"case": case.name, "error_type": type(exc).__name__},
                    )
                    if stop_on_failure:
                        return CaseResult(case, False, finding=finding)
                    continue
                if not result.passed:
                    finding = Finding(
                        invariant=invariant.name,
                        message=result.message or "Invariant violated",
                        trace=tuple(trace),
                        before=previous,
                        after=current,
                        metadata={"case": case.name, **(result.evidence or {}), **case.metadata},
                    )
                    if stop_on_failure:
                        return CaseResult(case, False, finding=finding)
            previous = current

        return CaseResult(case, True)

    def run(self, cases: Iterable[Case]) -> list[CaseResult]:
        return [self.run_case(case) for case in cases]
