from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReplayDecision:
    accepted: bool
    reason: str


class NonceReplayGuard:
    """Monotonic nonce guard for identities or signed protocol messages."""

    def __init__(self):
        self.highest: dict[str, int] = {}

    def check(self, identity: str, nonce: int) -> ReplayDecision:
        if nonce < 0:
            return ReplayDecision(False, "negative nonce")
        previous = self.highest.get(identity, -1)
        if nonce <= previous:
            return ReplayDecision(False, "replay or stale nonce")
        self.highest[identity] = nonce
        return ReplayDecision(True, "accepted")

    def reset(self, identity: str) -> None:
        self.highest.pop(identity, None)

    def snapshot(self) -> dict[str, int]:
        return dict(self.highest)
