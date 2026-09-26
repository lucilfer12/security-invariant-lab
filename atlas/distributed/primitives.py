from __future__ import annotations

from dataclasses import dataclass, field
import bisect
import hashlib

@dataclass
class LamportClock:
    value: int = 0

    def tick(self) -> int:
        self.value += 1
        return self.value

    def recv(self, other: int) -> int:
        self.value = max(self.value, other) + 1
        return self.value

@dataclass
class VectorClock:
    values: dict[str, int] = field(default_factory=dict)

    def tick(self, node: str) -> dict[str, int]:
        self.values[node] = self.values.get(node, 0) + 1
        return dict(self.values)

    def merge(self, other: dict[str, int]) -> dict[str, int]:
        for key, value in other.items():
            self.values[key] = max(self.values.get(key, 0), value)
        return dict(self.values)

    def compare(self, other: dict[str, int]) -> str:
        keys = set(self.values) | set(other)
        left = [self.values.get(k, 0) for k in keys]
        right = [other.get(k, 0) for k in keys]
        le = all(a <= b for a, b in zip(left, right))
        ge = all(a >= b for a, b in zip(left, right))
        return "before" if le and left != right else "after" if ge and left != right else "equal" if left == right else "concurrent"

class ConsistentHashRing:
    def __init__(self, replicas: int = 32):
        self.replicas = replicas
        self._keys: list[int] = []
        self._nodes: dict[int, str] = {}

    def add(self, node: str) -> None:
        for i in range(self.replicas):
            key = int.from_bytes(hashlib.sha256(f"{node}:{i}".encode()).digest()[:8], "big")
            self._nodes[key] = node
        self._keys = sorted(self._nodes)

    def get(self, key: str) -> str | None:
        if not self._keys:
            return None
        digest = hashlib.sha256(key.encode()).digest()
        h = int.from_bytes(digest[:8], "big")
        i = bisect.bisect_left(self._keys, h) % len(self._keys)
        return self._nodes[self._keys[i]]
