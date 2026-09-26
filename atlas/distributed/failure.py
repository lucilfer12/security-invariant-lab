from dataclasses import dataclass


@dataclass(frozen=True)
class FailureStatus:
    node_id: str
    missed: int
    suspected: bool


class PhiFailureDetector:
    """Bounded heartbeat-miss detector; deterministic reference, not a production phi estimator."""

    def __init__(self, threshold: int = 3):
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        self.threshold = threshold
        self._misses = {}

    def heartbeat(self, node_id: str):
        self._misses[node_id] = 0

    def tick(self, node_id: str):
        self._misses[node_id] = self._misses.get(node_id, 0) + 1
        return self.status(node_id)

    def status(self, node_id: str) -> FailureStatus:
        missed = self._misses.get(node_id, 0)
        return FailureStatus(node_id, missed, missed >= self.threshold)
