from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

@dataclass(frozen=True)
class VCPUState:
    vcpu_id: int
    registers: dict[str, int]
    rip: int
    flags: int

@dataclass(frozen=True)
class DeviceState:
    name: str
    state: dict[str, int | str | bool]

@dataclass(frozen=True)
class VMSnapshot:
    guest_id: str
    generation: int
    memory: bytes
    vcpus: tuple[VCPUState, ...]
    devices: tuple[DeviceState, ...]

    def digest(self) -> str:
        payload = {
            "guest_id": self.guest_id, "generation": self.generation,
            "memory": self.memory.hex(),
            "vcpus": [{"id": v.vcpu_id, "registers": v.registers,
                       "rip": v.rip, "flags": v.flags} for v in self.vcpus],
            "devices": [{"name": d.name, "state": d.state} for d in self.devices],
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

class SnapshotStore:
    def __init__(self):
        self._snapshots: dict[str, VMSnapshot] = {}

    def put(self, snapshot: VMSnapshot) -> str:
        digest = snapshot.digest()
        self._snapshots[digest] = snapshot
        return digest

    def get(self, digest: str) -> VMSnapshot:
        return self._snapshots[digest]

    def export(self, digest: str) -> bytes:
        snap = self.get(digest)
        return json.dumps({
            "guest_id": snap.guest_id, "generation": snap.generation,
            "memory": snap.memory.hex(),
            "vcpus": [{"vcpu_id": v.vcpu_id, "registers": v.registers,
                       "rip": v.rip, "flags": v.flags} for v in snap.vcpus],
            "devices": [{"name": d.name, "state": d.state} for d in snap.devices],
        }, sort_keys=True, separators=(",", ":")).encode()
