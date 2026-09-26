from __future__ import annotations

from dataclasses import dataclass, field
import heapq

@dataclass(frozen=True)
class Failure:
    tick: int
    target: int
    kind: str
    value: int | float | None = None

@dataclass(frozen=True)
class Request:
    tick: int
    request_id: int
    service: int
    payload_size: int

@dataclass
class Node:
    node_id: int
    up: bool = True
    cpu_capacity: int = 100
    memory_capacity: int = 1024
    cpu_used: int = 0
    memory_used: int = 0
    requests: int = 0

@dataclass
class SimulationStats:
    completed: int = 0
    dropped: int = 0
    failed_nodes: int = 0
    bytes_processed: int = 0

class GlobalSimulator:
    """Event-driven simulator sized for large deterministic node/service/request runs."""
    def __init__(self, nodes: int = 10_000, services: int = 100_000, seed: int = 1):
        if nodes <= 0 or services <= 0:
            raise ValueError("nodes and services must be positive")
        self.nodes = {i: Node(i) for i in range(nodes)}
        self.service_nodes = {service: service % nodes for service in range(services)}
        self.queue: list[tuple[int, int, object]] = []
        self.seq = 0
        self.now = 0
        self.stats = SimulationStats()
        self.seed = seed

    def schedule(self, event: Request | Failure) -> None:
        self.seq += 1
        heapq.heappush(self.queue, (event.tick, self.seq, event))
    def run(self, until: int) -> SimulationStats:
        while self.queue and self.queue[0][0] <= until:
            self.now, _, event = heapq.heappop(self.queue)
            if isinstance(event, Failure):
                node = self.nodes[event.target]
                node.up = event.kind != "down"
                self.stats.failed_nodes = sum(1 for n in self.nodes.values() if not n.up)
                continue
            node_id = self.service_nodes[event.service]
            node = self.nodes[node_id]
            if not node.up or event.payload_size < 0:
                self.stats.dropped += 1
                continue
            node.requests += 1
            self.stats.completed += 1
            self.stats.bytes_processed += event.payload_size
        return self.stats

    def inject_failure(self, tick: int, node: int, kind: str = "down") -> None:
        if node not in self.nodes:
            raise KeyError(node)
        self.schedule(Failure(tick, node, kind))
