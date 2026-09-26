from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import struct

class PacketError(ValueError):
    pass


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) | data[i + 1]
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF

@dataclass(frozen=True)
class IPv4Packet:
    source: ipaddress.IPv4Address
    destination: ipaddress.IPv4Address
    payload: bytes
    protocol: int = 17
    ttl: int = 64
    identification: int = 0
    flags_fragment: int = 0

    def encode(self) -> bytes:
        if not 0 <= self.ttl <= 255:
            raise PacketError("invalid TTL")
        if not 0 <= self.protocol <= 255:
            raise PacketError("invalid protocol")
        if len(self.payload) > 65515:
            raise PacketError("payload too large")
        total_length = 20 + len(self.payload)
        first = (4 << 4) | 5
        header = struct.pack(
            "!BBHHHBBH4s4s",
            first, 0, total_length, self.identification & 0xFFFF,
            self.flags_fragment & 0x1FFF, self.ttl, self.protocol, 0,
            self.source.packed, self.destination.packed,
        )
        return header[:10] + struct.pack("!H", checksum(header)) + header[12:] + self.payload

    @classmethod
    def decode(cls, raw: bytes) -> "IPv4Packet":
        if len(raw) < 20:
            raise PacketError("truncated IPv4 header")
        version_ihl, _, total_length, ident, flags_frag, ttl, proto, hdr_sum, src, dst = struct.unpack(
            "!BBHHHBBH4s4s", raw[:20]
        )
        version, ihl = version_ihl >> 4, version_ihl & 0x0F
        if version != 4 or ihl < 5:
            raise PacketError("invalid IPv4 version/IHL")
        header_len = ihl * 4
        if len(raw) < total_length or total_length < header_len:
            raise PacketError("invalid total length")
        header = raw[:header_len]
        if checksum(header) != 0:
            raise PacketError("bad IPv4 checksum")
        options = header[20:header_len]
        if options and any(options):
            pass
        return cls(
            ipaddress.IPv4Address(src), ipaddress.IPv4Address(dst),
            raw[header_len:total_length], proto, ttl, ident, flags_frag
        )

@dataclass(frozen=True)
class Route:
    network: ipaddress.IPv4Network
    next_hop: ipaddress.IPv4Address | None
    interface: str

class RoutingTable:
    def __init__(self) -> None:
        self._routes: list[Route] = []

    def add(self, network: str, interface: str, next_hop: str | None = None) -> None:
        route = Route(ipaddress.ip_network(network), None if next_hop is None else ipaddress.ip_address(next_hop), interface)
        self._routes.append(route)
        self._routes.sort(key=lambda r: r.network.prefixlen, reverse=True)

    def lookup(self, address: str) -> Route | None:
        target = ipaddress.ip_address(address)
        for route in self._routes:
            if target in route.network:
                return route
        return None
