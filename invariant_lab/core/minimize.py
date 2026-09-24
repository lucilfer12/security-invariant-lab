from __future__ import annotations

from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


def minimize_trace(events: Iterable[T], fails: Callable[[list[T]], bool]) -> list[T]:
    """Greedy delta-debugging minimizer for deterministic failing sequences."""
    current = list(events)
    if not current or not fails(current):
        return current

    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(current):
            candidate = current[:i] + current[i + 1 :]
            if candidate and fails(candidate):
                current = candidate
                changed = True
            else:
                i += 1
    return current
