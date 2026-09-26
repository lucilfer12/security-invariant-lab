from __future__ import annotations

from dataclasses import dataclass
import heapq
import hashlib
import json

@dataclass(frozen=True, order=True)
class PendingTransaction:
    sort_key: tuple[int, int, str]
    sender: str
    nonce: int
    gas_limit: int
    max_fee: int
    payload: bytes

    @property
    def txid(self) -> str:
        raw = json.dumps({
            "sender": self.sender, "nonce": self.nonce, "gas_limit": self.gas_limit,
            "max_fee": self.max_fee, "payload": self.payload.hex()
        }, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()

class Mempool:
    """Nonce-aware bounded mempool with fee priority and replacement protection."""
    def __init__(self, capacity: int = 4096, replacement_bump: int = 10):
        self.capacity = max(1, capacity)
        self.replacement_bump = max(1, replacement_bump)
        self._by_id: dict[str, PendingTransaction] = {}
        self._by_sender_nonce: dict[tuple[str, int], str] = {}
        self._heap: list[PendingTransaction] = []

    def add(self, tx: PendingTransaction) -> str:
        key = (tx.sender, tx.nonce)
        existing_id = self._by_sender_nonce.get(key)
        if existing_id is not None:
            existing = self._by_id[existing_id]
            required = existing.max_fee * (100 + self.replacement_bump) // 100
            if tx.max_fee < required:
                raise ValueError("replacement fee bump too small")
            self.remove(existing_id)
        if len(self._by_id) >= self.capacity:
            self.evict_lowest()
        txid = tx.txid
        self._by_id[txid] = tx
        self._by_sender_nonce[key] = txid
        heapq.heappush(self._heap, tx)
        return txid
    def remove(self, txid: str) -> bool:
        tx = self._by_id.pop(txid, None)
        if tx is None:
            return False
        self._by_sender_nonce.pop((tx.sender, tx.nonce), None)
        return True

    def evict_lowest(self) -> None:
        live = [tx for tx in self._heap if tx.txid in self._by_id]
        if not live:
            return
        victim = min(live, key=lambda tx: (tx.max_fee, tx.nonce, tx.sender))
        self.remove(victim.txid)

    def select(self, limit: int, base_fee: int = 0) -> list[PendingTransaction]:
        if limit <= 0:
            return []
        candidates = [tx for tx in self._by_id.values() if tx.max_fee >= base_fee]
        return sorted(candidates, key=lambda tx: (-tx.max_fee, tx.sender, tx.nonce))[:limit]

    def by_sender(self, sender: str) -> list[PendingTransaction]:
        return sorted((tx for tx in self._by_id.values() if tx.sender == sender),
                      key=lambda tx: tx.nonce)

    def __len__(self) -> int:
        return len(self._by_id)
