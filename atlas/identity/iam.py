from __future__ import annotations

from dataclasses import dataclass, field
import time

@dataclass(frozen=True)
class Principal:
    id: str
    kind: str = "user"

@dataclass(frozen=True)
class Role:
    name: str
    permissions: frozenset[str]

@dataclass(frozen=True)
class AuditEvent:
    ts: int
    principal: str
    action: str
    resource: str
    allowed: bool

@dataclass
class IAM:
    principals: dict[str, Principal] = field(default_factory=dict)
    roles: dict[str, Role] = field(default_factory=dict)
    bindings: dict[str, set[str]] = field(default_factory=dict)
    audit: list[AuditEvent] = field(default_factory=list)

    def allow(self, principal: str, action: str, resource: str) -> bool:
        permissions = {p for r in self.bindings.get(principal, set()) for p in self.roles[r].permissions}
        decision = f"{action}:{resource}" in permissions or f"{action}:*" in permissions or "*:*" in permissions
        self.audit.append(AuditEvent(time.time_ns(), principal, action, resource, decision))
        return decision
