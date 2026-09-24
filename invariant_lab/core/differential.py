from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class DifferentialMismatch:
    step: int
    left: Any
    right: Any
    message: str


def compare_sequences(events, left_apply: Callable[[Any, Any], None], right_apply: Callable[[Any, Any], None],
                      left_state: Any, right_state: Any, normalize: Callable[[Any], Any] | None = None):
    """Execute the same events against two implementations and report the first normalized mismatch."""
    normalize = normalize or (lambda x: x)
    mismatches: list[DifferentialMismatch] = []
    for index, event in enumerate(events):
        left_apply(left_state, event)
        right_apply(right_state, event)
        l = normalize(left_state)
        r = normalize(right_state)
        if l != r:
            mismatches.append(DifferentialMismatch(index, l, r, "normalized states diverged"))
            break
    return mismatches
