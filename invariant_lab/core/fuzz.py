from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Callable, Sequence, TypeVar

from .engine import Case, Engine
from .model import Event


T = TypeVar("T")


@dataclass(frozen=True)
class FuzzConfig:
    seed: int = 1337
    cases: int = 100
    max_length: int = 12


class SequenceFuzzer:
    """Deterministic event-sequence fuzzer for local models."""

    def __init__(self, event_factory: Callable[[random.Random], Event], config: FuzzConfig | None = None):
        self.event_factory = event_factory
        self.config = config or FuzzConfig()

    def cases(self) -> Sequence[Case]:
        rng = random.Random(self.config.seed)
        output: list[Case] = []
        for index in range(self.config.cases):
            length = rng.randint(1, self.config.max_length)
            events = tuple(self.event_factory(rng) for _ in range(length))
            output.append(Case(name=f"fuzz-{index:05d}", events=events, metadata={"seed": self.config.seed}))
        return output

    def run(self, engine: Engine):
        return engine.run(self.cases())
