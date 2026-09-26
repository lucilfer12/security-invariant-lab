from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
import time

class ContainerState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"

@dataclass(frozen=True)
class ResourceLimits:
    cpu_millis: int = 1000
    memory_bytes: int = 256 * 1024 * 1024
    pids: int = 64

@dataclass(frozen=True)
class ImageManifest:
    name: str
    version: str
    layers: tuple[str, ...]
    config_digest: str

    def digest(self) -> str:
        raw = json.dumps({
            "name": self.name, "version": self.version,
            "layers": list(self.layers), "config_digest": self.config_digest
        }, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()

@dataclass
class Container:
    id: str
    image: ImageManifest
    argv: tuple[str, ...]
    env: dict[str, str] = field(default_factory=dict)
    limits: ResourceLimits = field(default_factory=ResourceLimits)
    state: ContainerState = ContainerState.CREATED
    started_ns: int | None = None
    exit_code: int | None = None

class ContainerRuntime:
    """OCI-inspired lifecycle model with content identity and resource accounting."""
    def __init__(self):
        self.images: dict[str, ImageManifest] = {}
        self.containers: dict[str, Container] = {}

    def register_image(self, image: ImageManifest) -> str:
        digest = image.digest()
        self.images[digest] = image
        return digest

    def create(self, container_id: str, image_digest: str, argv: tuple[str, ...],
               env: dict[str, str] | None = None, limits: ResourceLimits | None = None) -> Container:
        if container_id in self.containers:
            raise ValueError("container already exists")
        if not argv:
            raise ValueError("argv cannot be empty")
        image = self.images.get(image_digest)
        if image is None:
            raise KeyError("unknown image digest")
        container = Container(container_id, image, argv, dict(env or {}),
                              limits or ResourceLimits())
        self.containers[container_id] = container
        return container
    def start(self, container_id: str) -> None:
        c = self.containers[container_id]
        if c.state is not ContainerState.CREATED:
            raise RuntimeError(f"cannot start from {c.state}")
        c.state = ContainerState.RUNNING
        c.started_ns = time.time_ns()
        c.exit_code = None

    def stop(self, container_id: str, exit_code: int = 0) -> None:
        c = self.containers[container_id]
        if c.state not in (ContainerState.RUNNING, ContainerState.CREATED):
            raise RuntimeError(f"cannot stop from {c.state}")
        c.state = ContainerState.STOPPED
        c.exit_code = exit_code

    def fail(self, container_id: str, exit_code: int = 1) -> None:
        c = self.containers[container_id]
        c.state = ContainerState.FAILED
        c.exit_code = exit_code

    def usage_snapshot(self, container_id: str, cpu_millis_used: int,
                       memory_bytes_used: int, pids_used: int) -> dict:
        c = self.containers[container_id]
        limits = c.limits
        return {
            "container": c.id,
            "state": c.state.value,
            "cpu_millis": cpu_millis_used,
            "cpu_limit": limits.cpu_millis,
            "memory_bytes": memory_bytes_used,
            "memory_limit": limits.memory_bytes,
            "pids": pids_used,
            "pids_limit": limits.pids,
            "within_limits": (
                0 <= cpu_millis_used <= limits.cpu_millis
                and 0 <= memory_bytes_used <= limits.memory_bytes
                and 0 <= pids_used <= limits.pids
            ),
        }

    def inspect(self, container_id: str) -> dict:
        c = self.containers[container_id]
        return {
            "id": c.id, "image": c.image.digest(), "argv": list(c.argv),
            "env": dict(c.env), "state": c.state.value,
            "limits": c.limits.__dict__.copy(), "exit_code": c.exit_code,
        }
