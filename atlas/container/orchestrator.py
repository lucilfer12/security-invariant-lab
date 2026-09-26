from __future__ import annotations

from dataclasses import dataclass
from .runtime import ContainerRuntime, ResourceLimits

@dataclass(frozen=True)
class Deployment:
    name: str
    image_digest: str
    argv: tuple[str, ...]
    replicas: int
    limits: ResourceLimits

class Orchestrator:
    """Declarative deployment controller layered over the ATLAS container runtime."""
    def __init__(self, runtime: ContainerRuntime):
        self.runtime = runtime
        self.deployments: dict[str, Deployment] = {}

    def apply(self, deployment: Deployment) -> list[str]:
        if deployment.replicas <= 0:
            raise ValueError("replicas must be positive")
        self.delete(deployment.name)
        ids = []
        for index in range(deployment.replicas):
            cid = f"{deployment.name}-{index}"
            self.runtime.create(cid, deployment.image_digest, deployment.argv, limits=deployment.limits)
            self.runtime.start(cid)
            ids.append(cid)
        self.deployments[deployment.name] = deployment
        return ids

    def scale(self, name: str, replicas: int) -> list[str]:
        deployment = self.deployments[name]
        return self.apply(Deployment(
            deployment.name, deployment.image_digest, deployment.argv, replicas, deployment.limits
        ))

    def delete(self, name: str) -> None:
        existing = self.deployments.pop(name, None)
        if existing is None:
            return
        for index in range(existing.replicas):
            cid = f"{name}-{index}"
            if cid in self.runtime.containers:
                container = self.runtime.containers[cid]
                if container.state.value in ("running", "created"):
                    self.runtime.stop(cid)
                del self.runtime.containers[cid]
