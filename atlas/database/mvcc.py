from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Transaction:
    id: int
    snapshot: int
    writes: dict[str, bytes]

class MVCCStore:
    def __init__(self):
        self.version = 0
        self.data: dict[str, tuple[int, bytes]] = {}
        self.next_tx = 1

    def begin(self) -> Transaction:
        tx = Transaction(self.next_tx, self.version, {})
        self.next_tx += 1
        return tx

    def read(self, tx: Transaction, key: str) -> bytes | None:
        item = self.data.get(key)
        return None if item is None or item[0] > tx.snapshot else item[1]

    def write(self, tx: Transaction, key: str, value: bytes) -> None:
        tx.writes[key] = value

    def commit(self, tx: Transaction) -> int:
        for key in tx.writes:
            item = self.data.get(key)
            if item is not None and item[0] > tx.snapshot:
                raise RuntimeError("serialization conflict")
        self.version += 1
        for key, value in tx.writes.items():
            self.data[key] = (self.version, value)
        return self.version
