from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class InvariantResult:
    passed: bool
    message: str = ""
    evidence: dict[str, Any] | None = None


class StateLike(Protocol):
    def snapshot(self, label: str = "state") -> Any: ...


class Invariant:
    """Base class for executable security invariants."""

    name = "unnamed"
    description = ""

    def check(self, state: StateLike) -> InvariantResult:
        raise NotImplementedError


class CallableInvariant(Invariant):
    def __init__(self, name: str, check, description: str = ""):
        self.name = name
        self.description = description
        self._check = check

    def check(self, state: StateLike) -> InvariantResult:
        result = self._check(state)
        if isinstance(result, InvariantResult):
            return result
        if isinstance(result, bool):
            return InvariantResult(result)
        raise TypeError(f"Invariant {self.name!r} returned unsupported value {type(result)!r}")
