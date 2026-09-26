from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Any

@dataclass(frozen=True)
class Counterexample:
    depth: int
    state: Any
    trace: tuple[Any, ...]

def bounded_check(initial: Any, transitions: Iterable[Callable[[Any], Any]],
                  invariant: Callable[[Any], bool], depth: int = 16) -> Counterexample | None:
    frontier = [(initial, ())]
    transitions = tuple(transitions)
    for step in range(depth + 1):
        next_frontier = []
        for state, trace in frontier:
            if not invariant(state):
                return Counterexample(step, state, trace)
            for transition in transitions:
                new_state = transition(state)
                next_frontier.append((new_state, trace + (new_state,)))
        frontier = next_frontier
    return None
