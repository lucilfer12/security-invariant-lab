from __future__ import annotations

from dataclasses import dataclass, field
import math

@dataclass
class Node:
    id: str
    cpu: int
    memory: int
    used_cpu: int = 0
    used_memory: int = 0

    def can_fit(self, cpu: int, memory: int) -> bool:
        return self.used_cpu + cpu <= self.cpu and self.used_memory + memory <= self.memory

    def place(self, cpu: int, memory: int) -> bool:
        if not self.can_fit(cpu, memory):
            return False
        self.used_cpu += cpu
        self.used_memory += memory
        return True

    def release(self, cpu: int, memory: int) -> None:
        self.used_cpu = max(0, self.used_cpu - cpu)
        self.used_memory = max(0, self.used_memory - memory)

@dataclass(frozen=True)
class Workload:
    id: str
    cpu: int
    memory: int
    replicas: int = 1

@dataclass
class Autoscaler:
    min_replicas: int
    max_replicas: int
    target_utilization: float = 0.7
    history: list[int] = field(default_factory=list)

    def desired(self, current: int, utilization: float) -> int:
        if not 0 < self.target_utilization <= 1:
            raise ValueError("target utilization must be in (0, 1]")
        if utilization < 0:
            raise ValueError("utilization cannot be negative")
        raw = math.ceil(current * utilization / self.target_utilization) if current else self.min_replicas
        desired = max(self.min_replicas, min(self.max_replicas, raw))
        self.history.append(desired)
        return desired
class Scheduler:
    """Deterministic bin-packing scheduler with explicit placement accounting."""
    def __init__(self, nodes: list[Node]):
        self.nodes = {node.id: node for node in nodes}
        self.placements: dict[str, str] = {}

    def schedule(self, workload: Workload) -> list[str]:
        if workload.replicas <= 0:
            raise ValueError("replicas must be positive")
        placements = []
        for index in range(workload.replicas):
            replica_id = f"{workload.id}#{index}"
            candidate = sorted(
                self.nodes.values(),
                key=lambda n: (
                    not n.can_fit(workload.cpu, workload.memory),
                    (n.cpu - n.used_cpu) + (n.memory - n.used_memory),
                    n.id,
                ),
            )
            placed = next((node for node in candidate if node.can_fit(workload.cpu, workload.memory)), None)
            if placed is None:
                for node_id in placements:
                    self.nodes[node_id].release(workload.cpu, workload.memory)
                raise RuntimeError("insufficient cluster capacity")
            placed.place(workload.cpu, workload.memory)
            self.placements[replica_id] = placed.id
            placements.append(placed.id)
        return placements

    def unschedule(self, workload: Workload) -> None:
        for index in range(workload.replicas):
            replica_id = f"{workload.id}#{index}"
            node_id = self.placements.pop(replica_id, None)
            if node_id is not None:
                self.nodes[node_id].release(workload.cpu, workload.memory)
