from pathlib import Path
from tempfile import TemporaryDirectory

from .ai import InferenceBatcher, Model, ModelRegistry
from .blockchain import Chain, Transaction
from .crypto import hkdf_expand, hmac_sha256, sha256
from .distributed import ConsistentHashRing, LamportClock, VectorClock
from .machine import Assembler, CPU
from .network import Packet, RouteTable, Router
from .observability import Counter, Tracer
from .protocol import Message, decode_message
from .security import Capability, CapabilityAuthority, parse_policy
from .storage import CAS, WAL

def run() -> None:
    code = Assembler().assemble("CONST r0, 2\nCONST r1, 3\nMUL r2, r0, r1\nHALT")
    cpu = CPU(); cpu.run(code); assert cpu.r[2] == 6
    assert parse_policy("allow role=admin action=read resource=*").decide("admin", "read", "x")
    clock = LamportClock(); assert clock.tick() == 1 and clock.recv(4) == 5
    vector = VectorClock(); vector.tick("a"); assert vector.compare({"a": 2}) == "before"
    ring = ConsistentHashRing(); ring.add("a"); ring.add("b"); assert ring.get("x") in {"a", "b"}
    with TemporaryDirectory() as td:
        cas = CAS(Path(td) / "cas"); digest = cas.put(b"atlas"); assert cas.get(digest) == b"atlas"
        wal = WAL(Path(td) / "wal"); wal.append("boot", {"ok": True}); assert wal.recover()[0]["kind"] == "boot"
    msg = Message(1, "ping", "1", {"x": 1}); assert decode_message(msg.canonical()) == msg
    authority = CapabilityAuthority(b"secret"); token = authority.issue(Capability("u", "read", "r", 9_999_999_999, "n"))
    assert authority.verify(token, "u", "read", "r", 0)
    assert len(hkdf_expand(hmac_sha256(b"k", b"m"), b"atlas", 32)) == 32 and sha256(b"x")
    assert Router(RouteTable({"10.": "n1"})).forward(Packet("a", "10.2", b"x"))[0] == "n1"
    chain = Chain(); chain.append([Transaction("alice", 0, {"v": 1})]); assert chain.verify()
    registry = ModelRegistry(); registry.register(Model("echo", "1", lambda xs: xs)); batch = InferenceBatcher(registry); batch.submit("echo", 7); assert batch.flush("echo") == [7]
    counter = Counter(); assert counter.inc(2) == 2
    tracer = Tracer(); span = tracer.span("boot"); span.finish(); assert span.end_ns is not None

if __name__ == "__main__":
    run(); print("ATLAS self-tests: PASS")
