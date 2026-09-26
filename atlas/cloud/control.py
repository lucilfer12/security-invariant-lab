from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(frozen=True)
class Quota:
    cpu: int
    memory: int
    storage: int

@dataclass(frozen=True)
class Resource:
    id: str
    kind: str
    cpu: int = 0
    memory: int = 0
    storage: int = 0

class CloudController:
    def __init__(self, quota: Quota):
        self.quota = quota
        self.resources: dict[str, Resource] = {}

    def usage(self) -> tuple[int, int, int]:
        return (sum(r.cpu for r in self.resources.values()),
                sum(r.memory for r in self.resources.values()),
                sum(r.storage for r in self.resources.values()))

    def create(self, resource: Resource) -> None:
        if resource.id in self.resources: raise ValueError("resource exists")
        used = self.usage()
        total = tuple(used[i] + (resource.cpu, resource.memory, resource.storage)[i] for i in range(3))
        limit = (self.quota.cpu, self.quota.memory, self.quota.storage)
        if any(total[i] > limit[i] for i in range(3)): raise RuntimeError("quota exceeded")
        self.resources[resource.id] = resource

    def delete(self, resource_id: str) -> None:
        del self.resources[resource_id]
