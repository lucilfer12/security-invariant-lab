from __future__ import annotations

from dataclasses import dataclass, field

@dataclass
class Guest:
    id: str
    memory: int
    vcpus: int
    running: bool = False
    registers: dict[str, int] = field(default_factory=dict)

class Hypervisor:
    def __init__(self):
        self.guests: dict[str, Guest] = {}

    def create(self, guest: Guest) -> None:
        if guest.id in self.guests:
            raise ValueError("guest already exists")
        self.guests[guest.id] = guest

    def start(self, guest_id: str) -> None:
        self.guests[guest_id].running = True

    def stop(self, guest_id: str) -> None:
        self.guests[guest_id].running = False

    def snapshot(self, guest_id: str) -> dict:
        guest = self.guests[guest_id]
        return {"id": guest.id, "memory": guest.memory, "vcpus": guest.vcpus,
                "running": guest.running, "registers": dict(guest.registers)}
