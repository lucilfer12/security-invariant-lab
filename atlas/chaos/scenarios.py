from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class FailureKind(str, Enum):
    NODE_DOWN = "node_down"
    PACKET_LOSS = "packet_loss"
    LATENCY = "latency"
    CLOCK_SKEW = "clock_skew"
    DISK_CORRUPTION = "disk_corruption"
    CPU_STARVATION = "cpu_starvation"
    MEMORY_PRESSURE = "memory_pressure"
    BYZANTINE = "byzantine"


@dataclass(frozen=True)
class FailureSpec:
    target: str
    kind: FailureKind
    magnitude: float = 1.0
    duration: int = 1

    def validate(self) -> None:
        if not self.target:
            raise ValueError("failure target is required")
        if self.magnitude < 0:
            raise ValueError("failure magnitude cannot be negative")
        if self.duration <= 0:
            raise ValueError("failure duration must be positive")


@dataclass
class FailurePlan:
    events: list[FailureSpec] = field(default_factory=list)

    def add(self, event: FailureSpec) -> None:
        event.validate()
        self.events.append(event)

    def active(self, tick: int) -> list[FailureSpec]:
        if tick < 0:
            raise ValueError("tick cannot be negative")
        return [event for event in self.events if tick < event.duration]

    def validate(self) -> bool:
        for event in self.events:
            event.validate()
        return True
