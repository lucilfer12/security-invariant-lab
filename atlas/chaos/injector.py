from __future__ import annotations

from dataclasses import dataclass
import random

@dataclass(frozen=True)
class ChaosEvent:
    target: str
    kind: str
    value: float | int | None = None

class ChaosInjector:
    def __init__(self, seed: int = 0):
        self.random = random.Random(seed)

    def inject(self, target: str, probabilities: dict[str, float]) -> ChaosEvent | None:
        for kind, probability in sorted(probabilities.items()):
            if not 0.0 <= probability <= 1.0:
                raise ValueError("probability outside [0,1]")
            if self.random.random() < probability:
                return ChaosEvent(target, kind)
        return None

    def fixed(self, target: str, kind: str, value: float | int | None = None) -> ChaosEvent:
        return ChaosEvent(target, kind, value)
