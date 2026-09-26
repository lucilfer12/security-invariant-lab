from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Action(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class Packet:
    src_ip: str
    dst_ip: str
    protocol: str
    src_port: int = 0
    dst_port: int = 0
    payload_size: int = 0


@dataclass(frozen=True)
class FirewallRule:
    action: Action
    protocol: str | None = None
    src_cidr: str | None = None
    dst_cidr: str | None = None
    dst_port: int | None = None


class Firewall:
    def __init__(self, rules: list[FirewallRule] | None = None, default: Action = Action.DENY):
        self.rules = list(rules or [])
        self.default = default

    def evaluate(self, packet: Packet) -> Action:
        for rule in self.rules:
            if rule.protocol and rule.protocol.lower() != packet.protocol.lower():
                continue
            if rule.dst_port is not None and rule.dst_port != packet.dst_port:
                continue
            if rule.src_cidr and not _in_cidr(packet.src_ip, rule.src_cidr):
                continue
            if rule.dst_cidr and not _in_cidr(packet.dst_ip, rule.dst_cidr):
                continue
            return rule.action
        return self.default


def _in_cidr(ip: str, cidr: str) -> bool:
    import ipaddress

    return ipaddress.ip_address(ip) in ipaddress.ip_network(cidr, strict=False)


@dataclass(frozen=True)
class NatBinding:
    private_ip: str
    private_port: int
    public_ip: str
    public_port: int
    protocol: str


class SourceNat:
    def __init__(self, public_ip: str, first_port: int = 40000):
        self.public_ip = public_ip
        self.next_port = first_port
        self.bindings: dict[tuple[str, int, str], NatBinding] = {}

    def translate(self, private_ip: str, private_port: int, protocol: str) -> NatBinding:
        key = (private_ip, private_port, protocol.lower())
        if key not in self.bindings:
            binding = NatBinding(private_ip, private_port, self.public_ip, self.next_port, protocol.lower())
            self.bindings[key] = binding
            self.next_port += 1
        return self.bindings[key]
