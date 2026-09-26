from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuorumResult:
    voters: frozenset[str]
    required: int
    reached: bool


class QuorumTracker:
    """Deterministic majority/quorum tracker for replicated operations."""

    def __init__(self, members: list[str], required: int | None = None):
        unique = list(dict.fromkeys(members))
        if not unique:
            raise ValueError("members cannot be empty")
        self.members = tuple(unique)
        self.required = required if required is not None else len(unique) // 2 + 1
        if not 1 <= self.required <= len(self.members):
            raise ValueError("invalid quorum size")
        self.voters: set[str] = set()

    def acknowledge(self, member: str) -> bool:
        if member in self.members:
            self.voters.add(member)
        return self.reached

    @property
    def reached(self) -> bool:
        return len(self.voters) >= self.required

    def result(self) -> QuorumResult:
        return QuorumResult(frozenset(self.voters), self.required, self.reached)

    def reset(self) -> None:
        self.voters.clear()
