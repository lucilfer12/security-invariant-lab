from __future__ import annotations

from dataclasses import dataclass, field
import bisect
import math

@dataclass
class HDRHistogram:
    bounds: tuple[float, ...]
    counts: list[int] = field(init=False)
    total: int = 0
    sum: float = 0.0

    def __post_init__(self):
        if not self.bounds or tuple(sorted(self.bounds)) != self.bounds:
            raise ValueError("bounds must be non-empty and sorted")
        self.counts = [0] * (len(self.bounds) + 1)

    def observe(self, value: float) -> None:
        if not math.isfinite(value) or value < 0:
            raise ValueError("histogram value must be finite and non-negative")
        index = bisect.bisect_left(self.bounds, value)
        self.counts[index] += 1
        self.total += 1
        self.sum += value

    def quantile(self, q: float) -> float:
        if not 0 <= q <= 1:
            raise ValueError("quantile must be in [0, 1]")
        if not self.total:
            return float("nan")
        target = max(1, math.ceil(q * self.total))
        seen = 0
        for index, count in enumerate(self.counts):
            seen += count
            if seen >= target:
                return self.bounds[index] if index < len(self.bounds) else self.bounds[-1]
        return self.bounds[-1]

    @property
    def mean(self) -> float:
        return self.sum / self.total if self.total else float("nan")
