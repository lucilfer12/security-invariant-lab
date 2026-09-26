from __future__ import annotations

from atlas.blockchain.state import StateError, StateMachine, Transfer
from atlas.network.dns import DNSQuestion, DNSRecord, build_query, decode_address, encode_address
from atlas.formal.symbolic_exec import Path, SymbolicExecutor
from atlas.container.runtime import ContainerRuntime, ImageManifest, ResourceLimits
from atlas.container.orchestrator import Deployment, Orchestrator
from atlas.hypervisor.migration import LiveMigration
from atlas.hypervisor.snapshot import DeviceState, SnapshotStore, VCPUState, VMSnapshot

def test_state_machine_transfer_and_root():
    state = StateMachine()
    state.fund("alice", 100)
    state.apply(Transfer("alice", "bob", 30, 0))
    assert state.account("alice").balance == 70
    assert state.account("alice").nonce == 1
    assert state.account("bob").balance == 30
    assert len(state.state_root()) == 64


def test_dns_query_and_a_record_roundtrip():
    query = build_query(7, DNSQuestion("example.com"))
    assert query[:2] == b"\x00\x07"
    raw = encode_address(DNSRecord("example.com", 1, 60, "192.0.2.1"))
    record, end = decode_address(raw, 0)
    assert record.address == "192.0.2.1"
    assert end == len(raw)


def test_symbolic_executor_finds_violation():
    sx = SymbolicExecutor()
    x = sx.symbol("x")
    initial = Path([x >= 0, x <= 10], ["entry"])
    result = sx.find_assertion_violation(initial, x < 5, "x-bound")
    assert result.status == "sat"
    assert result.model["x"] >= 5
def test_orchestrator_rollout_and_scale():
    runtime = ContainerRuntime()
    image = ImageManifest("worker", "1", ("sha256:1",), "sha256:c")
    digest = runtime.register_image(image)
    orch = Orchestrator(runtime)
    ids = orch.apply(Deployment("worker", digest, ("run",), 2, ResourceLimits()))
    assert ids == ["worker-0", "worker-1"]
    assert all(runtime.containers[i].state.value == "running" for i in ids)
    orch.scale("worker", 3)
    assert len([c for c in runtime.containers if c.startswith("worker-")]) == 3


def test_vm_migration_preserves_content_digest():
    source = SnapshotStore()
    destination = SnapshotStore()
    snap = VMSnapshot(
        "guest-1", 4, b"pages",
        (VCPUState(0, {"rip": 99}, 99, 2),),
        (DeviceState("nic", {"link": True}),),
    )
    migration = LiveMigration(source, destination)
    ticket = migration.pre_copy(snap, "node-a", "node-b")
    assert migration.verify(ticket)
