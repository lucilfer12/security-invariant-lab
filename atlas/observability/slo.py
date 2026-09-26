from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SLOResult:
    total: int
    good: int
    target: float

    @property
    def availability(self) -> float:
        return self.good / self.total if self.total else 1.0

    @property
    def error_budget_remaining(self) -> float:
        return max(0.0, self.target - (1.0 - self.availability))

    @property
    def compliant(self) -> bool:
        return self.availability >= self.target


class SLOTracker:
    """Windowed availability/error-budget accounting."""

    def __init__(self, target: float = 0.999):
        if not 0.0 < target <= 1.0:
            raise ValueError("target must be in (0, 1]")
        self.target = target
        self.total = 0
        self.good = 0

    def observe(self, success: bool) -> None:
        self.total += 1
        if success:
            self.good += 1

    def result(self) -> SLOResult:
        return SLOResult(self.total, self.good, self.target)

    def reset(self) -> None:
        self.total = 0
        self.good = 0
