from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(frozen=True)
class SandboxSpec:
    name: str
    command: tuple[str, ...]
    env: dict[str, str] = field(default_factory=dict)
    read_only: bool = True

@dataclass
class Sandbox:
    spec: SandboxSpec
    state: str = "created"

    def start(self) -> None:
        if not self.spec.command:
            raise ValueError("sandbox command cannot be empty")
        self.state = "running"

    def stop(self) -> None:
        self.state = "stopped"

    def inspect(self) -> dict:
        return {"name": self.spec.name, "state": self.state,
                "command": list(self.spec.command), "read_only": self.spec.read_only}
