from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Delegation:
    issuer: str
    delegate: str
    permissions: frozenset[str]
    depth: int = 0

    def child(self, delegate: str, permissions: frozenset[str]) -> "Delegation":
        if self.depth >= 8:
            raise PermissionError("delegation depth exceeded")
        if not permissions <= self.permissions:
            raise PermissionError("delegation exceeds issuer scope")
        return Delegation(self.delegate, delegate, permissions, self.depth + 1)
