from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Callable

from .engine import Case, Engine
from .model import Event

@dataclass(frozen=True)
class AdaptiveConfig:
    seed: int = 1337
    cases: int = 250
    max_length: int = 24
    corpus_limit: int = 128

@dataclass(frozen=True)
class FuzzTelemetry:
    generated_cases: int
    unique_event_sequences: int
    failing_cases: int
    corpus_size: int

def _sequence_key(events: tuple[Event, ...]) -> str:
    raw = repr(tuple(e.to_dict() for e in events)).encode()
    return hashlib.sha256(raw).hexdigest()[:16]

class AdaptiveSequenceFuzzer:
    def __init__(self, event_factory: Callable[[random.Random], Event], config: AdaptiveConfig | None = None):
        self.event_factory = event_factory
        self.config = config or AdaptiveConfig()
        self.corpus: dict[str, tuple[Event, ...]] = {}
    def _mutate(self, base: tuple[Event, ...], rng: random.Random) -> tuple[Event, ...]:
        events = list(base)
        roll = rng.random()
        if not events or roll < 0.4:
            events.insert(rng.randrange(len(events) + 1), self.event_factory(rng))
        elif roll < 0.78:
            events[rng.randrange(len(events))] = self.event_factory(rng)
        elif len(events) > 1:
            del events[rng.randrange(len(events))]
        if len(events) > self.config.max_length:
            start = rng.randrange(len(events) - self.config.max_length + 1)
            events = events[start:start + self.config.max_length]
        return tuple(events)

    def cases(self) -> list[Case]:
        rng = random.Random(self.config.seed)
        generated: list[Case] = []
        seeds: list[tuple[Event, ...]] = [
            tuple(self.event_factory(rng) for _ in range(rng.randint(1, min(4, self.config.max_length))))
        ]
        for index in range(self.config.cases):
            pool = list(self.corpus.values()) or seeds
            base = rng.choice(pool)
            events = self._mutate(base, rng) if rng.random() < 0.85 else base
            key = _sequence_key(events)
            self.corpus.setdefault(key, events)
            if len(self.corpus) > self.config.corpus_limit:
                oldest = next(iter(self.corpus))
                self.corpus.pop(oldest)
            generated.append(Case(
                name=f"adaptive-{index:05d}",
                events=events,
                metadata={"seed": self.config.seed, "strategy": "state-corpus"},
            ))
            seeds.append(events)
        return generated

    def run(self, engine: Engine) -> tuple[list, FuzzTelemetry]:
        cases = self.cases()
        results = engine.run(cases)
        telemetry = FuzzTelemetry(
            generated_cases=len(cases),
            unique_event_sequences=len(self.corpus),
            failing_cases=sum(1 for r in results if not r.passed),
            corpus_size=len(self.corpus),
        )
        return results, telemetry

__all__ = ["AdaptiveConfig", "AdaptiveSequenceFuzzer", "FuzzTelemetry"]
