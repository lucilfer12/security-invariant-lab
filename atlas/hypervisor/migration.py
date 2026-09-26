from __future__ import annotations

from dataclasses import dataclass
from .snapshot import SnapshotStore, VMSnapshot

@dataclass(frozen=True)
class MigrationTicket:
    guest_id: str
    snapshot_digest: str
    source: str
    destination: str

class LiveMigration:
    """Checkpoint-and-transfer migration model with digest-based integrity checks."""
    def __init__(self, source: SnapshotStore, destination: SnapshotStore):
        self.source = source
        self.destination = destination

    def pre_copy(self, snapshot: VMSnapshot, source: str, destination: str) -> MigrationTicket:
        digest = self.source.put(snapshot)
        exported = self.source.export(digest)
        imported = __import__("json").loads(exported.decode())
        if imported["guest_id"] != snapshot.guest_id:
            raise RuntimeError("migration payload identity mismatch")
        remote_digest = self.destination.put(snapshot)
        if remote_digest != digest:
            raise RuntimeError("migration integrity check failed")
        return MigrationTicket(snapshot.guest_id, digest, source, destination)

    def verify(self, ticket: MigrationTicket) -> bool:
        return self.destination.get(ticket.snapshot_digest).guest_id == ticket.guest_id
