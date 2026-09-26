from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class BridgeMessage:
    source_chain: int
    destination_chain: int
    nonce: int
    sender: str
    recipient: str
    payload: bytes

class ReplayError(RuntimeError):
    pass

class BridgeVerifier:
    """Cross-chain replay protection keyed by source, sender and monotonically unique nonce."""
    def __init__(self):
        self.used: set[tuple[int, str, int]] = set()

    def verify(self, message: BridgeMessage) -> bool:
        key = (message.source_chain, message.sender, message.nonce)
        if message.source_chain == message.destination_chain:
            raise ValueError("source and destination chains must differ")
        if not message.sender or not message.recipient:
            raise ValueError("bridge participants are required")
        if message.nonce < 0:
            raise ValueError("nonce must be non-negative")
        if key in self.used:
            raise ReplayError("bridge message replay detected")
        self.used.add(key)
        return True
