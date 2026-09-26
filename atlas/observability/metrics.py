from __future__ import annotations

from dataclasses import dataclass, field

@dataclass
class Histogram:
    buckets: list[float] = field(default_factory=lambda: [0.001, 0.01, 0.1, 1.0, 10.0])
    counts: list[int] = field(default_factory=lambda: [0] * 5)
    total: int = 0
    sum: float = 0.0

    def observe(self, value: float) -> None:
        self.total += 1; self.sum += value
        for i, bound in enumerate(self.buckets):
            if value <= bound:
                self.counts[i] += 1
                break

    def mean(self) -> float:
        return self.sum / self.total if self.total else 0.0

@dataclass
class Registry:
    counters: dict[str, int] = field(default_factory=dict)
    histograms: dict[str, Histogram] = field(default_factory=dict)

    def inc(self, name: str, amount: int = 1) -> int:
        self.counters[name] = self.counters.get(name, 0) + amount
        return self.counters[name]
