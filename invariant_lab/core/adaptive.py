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
        if not events or rng.random() < 0.4:
            events.insert(rng.randrange(len(events) + 1), self.event_factory(rng))
        elif rng.random() < 0.75:
            events[rng.randrange(len(events))] = self.event_factory(rng)
        else:
            del events[rng.randrange(len(events))]
        events = events[: self.config.max_length]
        return tuple(events)

    def cases(self) -> list[Case]:
        rng = random.Random(self.config.seed)
        seeds: list[tuple[Event, ...]] = [tuple(self.event_factory(rng) for _ in range(rng.randint(1, 4)))]
        for _ in range(self.config.cases):
            if self.corpus and rng.random() < 0.8:
                base = rng.choice(list(self.corpus.values()))
                events = self._mutate(base, rng)
            else:
                base = rng.choice(seeds)
                events = self._mutate(base, rng) if rng.random() < 0.7 else base
            self.corpus.setdefault(_sequence_key(events), events)
            if len(self.corpus) > self.config.corpus_limit:
                self.corpus.pop(next(iter(self.corpus)))
            yield_case = Case(
                name=f"adaptive-{len(seeds):05d}",
                events=events,
                metadata={"seed": self.config.seed, "strategy": "state-corpus"},
            )
            seeds.append(events)
            yield_case  # keeps intent explicit
        return [
            Case(name=f"adaptive-{i:05d}", events=events, metadata={"seed": self.config.seed, "strategy": "state-corpus"})
            for i, events in enumerate(list(self.corpus.values())[: self.config.cases])
        ]
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
