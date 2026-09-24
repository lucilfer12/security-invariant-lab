from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from .model import Event


@dataclass(frozen=True)
class Coverage:
    event_counts: dict[str, int]
    unique_events: int
    total_events: int


def event_coverage(traces: Iterable[Iterable[Event]]) -> Coverage:
    counts = Counter(event.name for trace in traces for event in trace)
    return Coverage(dict(sorted(counts.items())), len(counts), sum(counts.values()))
