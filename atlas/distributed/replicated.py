from __future__ import annotations

from dataclasses import dataclass, field
import hashlib

@dataclass
class Replica:
    id: str
    data: dict[str, bytes] = field(default_factory=dict)
    online: bool = True
    applied_index: int = 0

@dataclass(frozen=True)
class LogEntry:
    index: int
    key: str
    value: bytes

class ReplicatedKV:
    """Primary/replica replication model with quorum acknowledgement and catch-up."""
    def __init__(self, replicas: list[str], write_quorum: int | None = None):
        if not replicas:
            raise ValueError("at least one replica is required")
        self.replicas = {rid: Replica(rid) for rid in replicas}
        self.primary = replicas[0]
        self.log: list[LogEntry] = []
        self.quorum = write_quorum or (len(replicas) // 2 + 1)

    def set_online(self, replica_id: str, online: bool) -> None:
        self.replicas[replica_id].online = online

    def put(self, key: str, value: bytes) -> int:
        if not key:
            raise ValueError("key cannot be empty")
        if not self.replicas[self.primary].online:
            raise RuntimeError("primary is offline")
        index = len(self.log) + 1
        entry = LogEntry(index, key, value)
        self.log.append(entry)
        acknowledgements = 0
        for replica in self.replicas.values():
            if replica.online:
                replica.data[key] = value
                replica.applied_index = index
                acknowledgements += 1
        if acknowledgements < self.quorum:
            self.log.pop()
            raise RuntimeError("write quorum unavailable")
        return index
    def catch_up(self, replica_id: str) -> int:
        replica = self.replicas[replica_id]
        if not replica.online:
            return replica.applied_index
        for entry in self.log[replica.applied_index:]:
            replica.data[entry.key] = entry.value
            replica.applied_index = entry.index
        return replica.applied_index

    def get(self, key: str, replica_id: str | None = None) -> bytes | None:
        rid = self.primary if replica_id is None else replica_id
        return self.replicas[rid].data.get(key)

    def shard_for(self, key: str, shards: int) -> int:
        if shards <= 0:
            raise ValueError("shards must be positive")
        digest = hashlib.sha256(key.encode()).digest()
        return int.from_bytes(digest[:8], "big") % shards

    def lag(self, replica_id: str) -> int:
        return len(self.log) - self.replicas[replica_id].applied_index
