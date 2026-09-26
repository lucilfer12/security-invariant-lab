from __future__ import annotations

from dataclasses import dataclass
import ipaddress
import struct

class DNSError(ValueError):
    pass

@dataclass(frozen=True)
class DNSQuestion:
    name: str
    qtype: int = 1
    qclass: int = 1

@dataclass(frozen=True)
class DNSRecord:
    name: str
    rtype: int
    ttl: int
    address: str

def encode_name(name: str) -> bytes:
    labels = name.rstrip(".").split(".")
    if any(not label or len(label) > 63 for label in labels):
        raise DNSError("invalid DNS label")
    raw = b"".join(bytes([len(label)]) + label.encode("idna") for label in labels)
    return raw + b"\x00"

def decode_name(packet: bytes, offset: int = 0) -> tuple[str, int]:
    labels = []
    pos = offset
    while True:
        if pos >= len(packet):
            raise DNSError("truncated DNS name")
        length = packet[pos]
        pos += 1
        if length == 0:
            return ".".join(labels) or ".", pos
        if length & 0xC0:
            raise DNSError("compression pointers not handled by minimal decoder")
        if pos + length > len(packet):
            raise DNSError("truncated DNS label")
        labels.append(packet[pos:pos + length].decode("idna"))
        pos += length

def build_query(transaction_id: int, question: DNSQuestion) -> bytes:
    header = struct.pack("!HHHHHH", transaction_id & 0xFFFF, 0x0100, 1, 0, 0, 0)
    return header + encode_name(question.name) + struct.pack("!HH", question.qtype, question.qclass)

def encode_address(record: DNSRecord) -> bytes:
    name = encode_name(record.name)
    if record.rtype == 1:
        address = ipaddress.IPv4Address(record.address).packed
    elif record.rtype == 28:
        address = ipaddress.IPv6Address(record.address).packed
    else:
        raise DNSError("only A and AAAA records are supported")
    return name + struct.pack("!HHIH", record.rtype, 1, record.ttl, len(address)) + address

def decode_address(packet: bytes, offset: int) -> tuple[DNSRecord, int]:
    name, pos = decode_name(packet, offset)
    if pos + 10 > len(packet):
        raise DNSError("truncated DNS record")
    rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", packet[pos:pos + 10])
    pos += 10
    if pos + rdlength > len(packet):
        raise DNSError("truncated DNS RDATA")
    payload = packet[pos:pos + rdlength]
    pos += rdlength
    if rclass != 1:
        raise DNSError("only IN class is supported")
    if rtype == 1 and rdlength == 4:
        address = str(ipaddress.IPv4Address(payload))
    elif rtype == 28 and rdlength == 16:
        address = str(ipaddress.IPv6Address(payload))
    else:
        raise DNSError("unsupported address record")
    return DNSRecord(name, rtype, ttl, address), pos
