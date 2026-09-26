from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json

class EventKind(str, Enum):
    AUTH = "auth"
    NETWORK = "network"
    PROCESS = "process"
    FILE = "file"
    POLICY = "policy"

@dataclass(frozen=True)
class SecurityEvent:
    timestamp_ns: int
    kind: EventKind
    actor: str
    action: str
    resource: str
    metadata: dict[str, str]
    event_id: str

    @classmethod
    def create(cls, timestamp_ns: int, kind: EventKind, actor: str,
               action: str, resource: str, metadata: dict[str, str] | None = None):
        body = json.dumps(
            {"ts": timestamp_ns, "kind": kind.value, "actor": actor,
             "action": action, "resource": resource, "metadata": metadata or {}},
            sort_keys=True, separators=(",", ":"),
        ).encode()
        return cls(timestamp_ns, kind, actor, action, resource,
                   dict(metadata or {}), hashlib.sha256(body).hexdigest())

@dataclass
class EvidenceLog:
    events: list[SecurityEvent]

    def append(self, event: SecurityEvent) -> None:
        self.events.append(event)

    def query(self, actor: str | None = None, kind: EventKind | None = None) -> list[SecurityEvent]:
        return [
            e for e in self.events
            if (actor is None or e.actor == actor) and (kind is None or e.kind is kind)
        ]

    def timeline(self) -> list[SecurityEvent]:
        return sorted(self.events, key=lambda e: (e.timestamp_ns, e.event_id))

    def verify_integrity(self) -> bool:
        for event in self.events:
            regenerated = SecurityEvent.create(
                event.timestamp_ns, event.kind, event.actor,
                event.action, event.resource, event.metadata,
            )
            if regenerated.event_id != event.event_id:
                return False
        return True
