from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from threading import RLock

class IsolationLevel(str, Enum):
    SNAPSHOT = "snapshot"
    SERIALIZABLE = "serializable"

@dataclass
class Transaction:
    txid: int
    snapshot: int
    isolation: IsolationLevel
    reads: set[str] = field(default_factory=set)
    writes: dict[str, bytes | None] = field(default_factory=dict)
    active: bool = True

class TransactionConflict(RuntimeError):
    pass

class SerializableStore:
    """MVCC transaction coordinator with first-committer-wins conflict detection."""
    def __init__(self):
        self._version = 0
        self._next_txid = 1
        self._data: dict[str, tuple[int, bytes | None]] = {}
        self._lock = RLock()

    def begin(self, isolation: IsolationLevel = IsolationLevel.SERIALIZABLE) -> Transaction:
        with self._lock:
            tx = Transaction(self._next_txid, self._version, isolation)
            self._next_txid += 1
            return tx

    def read(self, tx: Transaction, key: str) -> bytes | None:
        self._assert_active(tx)
        tx.reads.add(key)
        if key in tx.writes:
            return tx.writes[key]
        item = self._data.get(key)
        if item is None or item[0] > tx.snapshot:
            return None
        return item[1]

    def write(self, tx: Transaction, key: str, value: bytes) -> None:
        self._assert_active(tx)
        if not key:
            raise ValueError("key cannot be empty")
        tx.writes[key] = value
    def delete(self, tx: Transaction, key: str) -> None:
        self._assert_active(tx)
        tx.writes[key] = None

    def commit(self, tx: Transaction) -> int:
        self._assert_active(tx)
        with self._lock:
            changed_since_snapshot = {k for k, (ver, _) in self._data.items()
                                      if ver > tx.snapshot}
            if tx.isolation is IsolationLevel.SERIALIZABLE:
                if changed_since_snapshot & (tx.reads | set(tx.writes)):
                    tx.active = False
                    raise TransactionConflict("serialization failure")
            elif changed_since_snapshot & set(tx.writes):
                tx.active = False
                raise TransactionConflict("write-write conflict")
            self._version += 1
            for key, value in tx.writes.items():
                self._data[key] = (self._version, value)
            tx.active = False
            return self._version

    def rollback(self, tx: Transaction) -> None:
        self._assert_active(tx)
        tx.active = False
        tx.writes.clear()
        tx.reads.clear()

    def current_version(self) -> int:
        with self._lock:
            return self._version

    def dump(self) -> dict[str, bytes | None]:
        with self._lock:
            return {k: v for k, (_, v) in self._data.items()}

    @staticmethod
    def _assert_active(tx: Transaction) -> None:
        if not tx.active:
            raise RuntimeError("transaction is not active")
