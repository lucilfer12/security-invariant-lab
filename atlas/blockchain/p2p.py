from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
import hashlib

@dataclass(frozen=True)
class Peer:
    peer_id: str
    address: str
    score: int = 0

@dataclass(frozen=True)
class GossipMessage:
    topic: str
    message_id: str
    payload: bytes

@dataclass
class PeerTable:
    peers: dict[str, Peer] = field(default_factory=dict)

    def add(self, peer: Peer) -> None:
        self.peers[peer.peer_id] = peer

    def choose(self, limit: int = 8) -> list[Peer]:
        return sorted(self.peers.values(), key=lambda p: (-p.score, p.peer_id))[:limit]

class GossipNode:
    """Deterministic deduplicating gossip layer for block/transaction dissemination."""
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.peers = PeerTable()
        self.seen: set[str] = set()
        self.outbox: deque[tuple[str, GossipMessage]] = deque()

    @staticmethod
    def message_id(topic: str, payload: bytes) -> str:
        return hashlib.sha256(topic.encode() + b"\x00" + payload).hexdigest()

    def receive(self, topic: str, payload: bytes) -> GossipMessage | None:
        message = GossipMessage(topic, self.message_id(topic, payload), payload)
        if message.message_id in self.seen:
            return None
        self.seen.add(message.message_id)
        for peer in self.peers.choose():
            self.outbox.append((peer.peer_id, message))
        return message

    def drain(self) -> list[tuple[str, GossipMessage]]:
        out = list(self.outbox)
        self.outbox.clear()
        return out
