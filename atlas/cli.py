from __future__ import annotations

import argparse
import json
from pathlib import Path

from .distributed import ConsistentHashRing
from .machine import Assembler, CPU, disassemble
from .manifest import default_manifest
from .platform import AtlasPlatform
from .security import Capability, CapabilityAuthority, parse_policy

def self_test() -> dict:
    code = Assembler().assemble("CONST r0, 7\nCONST r1, 5\nADD r2, r0, r1\nHALT")
    cpu = CPU()
    cpu.run(code)
    ring = ConsistentHashRing()
    ring.add("node-a")
    ring.add("node-b")
    authority = CapabilityAuthority(b"atlas-test")
    token = authority.issue(Capability("u", "read", "x", 9_999_999_999, "n"))
    return {"isa_result": cpu.r[2], "instructions": len(code),
            "routing_sample": ring.get("atlas"),
            "policy": parse_policy("allow role=admin action=read resource=*").decide("admin", "read", "x"),
            "capability": authority.verify(token, "u", "read", "x", 0)}

def main() -> int:
    parser = argparse.ArgumentParser(prog="atlas")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("manifest")
    sub.add_parser("self-test")
    sub.add_parser("health")
    asm = sub.add_parser("asm"); asm.add_argument("file", type=Path)
    pol = sub.add_parser("policy"); pol.add_argument("file", type=Path)
    pol.add_argument("role"); pol.add_argument("action"); pol.add_argument("resource")
    args = parser.parse_args()
    if args.cmd == "manifest": print(default_manifest().to_json(), end="")
    elif args.cmd == "self-test": print(json.dumps(self_test(), indent=2))
    elif args.cmd == "health": print(json.dumps(AtlasPlatform().health(), indent=2))
    elif args.cmd == "asm": print(disassemble(Assembler().assemble(args.file.read_text())))
    elif args.cmd == "policy": print(json.dumps({"allow": parse_policy(args.file.read_text()).decide(args.role, args.action, args.resource)}))
    return 0
