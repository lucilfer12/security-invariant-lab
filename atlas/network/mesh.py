from __future__ import annotations

from dataclasses import dataclass, field
import random

@dataclass(frozen=True)
class Endpoint:
    name: str
    address: str
    weight: int = 1
    healthy: bool = True

@dataclass
class Service:
    name: str
    endpoints: list[Endpoint] = field(default_factory=list)
    rr_cursor: int = 0

    def choose(self) -> Endpoint:
        candidates = [e for e in self.endpoints if e.healthy and e.weight > 0]
        if not candidates:
            raise RuntimeError("no healthy endpoints")
        total = sum(e.weight for e in candidates)
        ticket = random.randint(1, total)
        for endpoint in candidates:
            ticket -= endpoint.weight
            if ticket <= 0:
                return endpoint
        return candidates[-1]

class ServiceMesh:
    def __init__(self, seed: int = 1):
        self.services: dict[str, Service] = {}
        self._random = random.Random(seed)

    def register(self, service: Service) -> None:
        self.services[service.name] = service

    def route(self, service_name: str) -> Endpoint:
        service = self.services[service_name]
        candidates = [e for e in service.endpoints if e.healthy and e.weight > 0]
        if not candidates:
            raise RuntimeError("no healthy endpoints")
        total = sum(e.weight for e in candidates)
        ticket = self._random.randint(1, total)
        for endpoint in candidates:
            ticket -= endpoint.weight
            if ticket <= 0:
                return endpoint
        return candidates[-1]

    def health(self, service_name: str) -> dict[str, int]:
        service = self.services[service_name]
        return {
            "total": len(service.endpoints),
            "healthy": sum(1 for e in service.endpoints if e.healthy),
        }
