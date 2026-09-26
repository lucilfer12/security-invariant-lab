from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class CausalOrder(str, Enum):
    BEFORE = "before"
    AFTER = "after"
    EQUAL = "equal"
    CONCURRENT = "concurrent"


@dataclass
class LamportClock:
    value: int = 0

    def tick(self) -> int:
        self.value += 1
        return self.value

    def send(self) -> int:
        return self.tick()

    def receive(self, remote: int) -> int:
        self.value = max(self.value, int(remote)) + 1
        return self.value


@dataclass
class VectorClock:
    values: dict[str, int] = field(default_factory=dict)

    def tick(self, node: str) -> dict[str, int]:
        self.values[node] = self.values.get(node, 0) + 1
        return dict(self.values)

    def merge(self, remote: dict[str, int]) -> dict[str, int]:
        for node, value in remote.items():
            self.values[node] = max(self.values.get(node, 0), int(value))
        return dict(self.values)

    def snapshot(self) -> dict[str, int]:
        return dict(self.values)


def compare_vectors(left: dict[str, int], right: dict[str, int]) -> CausalOrder:
    keys = set(left) | set(right)
    left_le = all(left.get(k, 0) <= right.get(k, 0) for k in keys)
    right_le = all(right.get(k, 0) <= left.get(k, 0) for k in keys)
    if left_le and right_le:
        return CausalOrder.EQUAL
    if left_le:
        return CausalOrder.BEFORE
    if right_le:
        return CausalOrder.AFTER
    return CausalOrder.CONCURRENT
