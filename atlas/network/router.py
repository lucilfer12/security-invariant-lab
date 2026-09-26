from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Packet:
    src: str
    dst: str
    payload: bytes
    ttl: int = 16

@dataclass
class RouteTable:
    routes: dict[str, str]

    def lookup(self, address: str) -> str | None:
        best = None
        for prefix, next_hop in self.routes.items():
            if address == prefix or address.startswith(prefix.rstrip("*")):
                if best is None or len(prefix) > len(best[0]):
                    best = (prefix, next_hop)
        return None if best is None else best[1]

class Router:
    def __init__(self, table: RouteTable):
        self.table = table

    def forward(self, packet: Packet) -> tuple[str, Packet] | None:
        if packet.ttl <= 0:
            return None
        hop = self.table.lookup(packet.dst)
        return None if hop is None else (hop, Packet(packet.src, packet.dst, packet.payload, packet.ttl - 1))
