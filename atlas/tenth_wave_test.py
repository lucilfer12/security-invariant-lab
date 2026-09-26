def test_global_simulator_scales_event_processing():
    from atlas.sim.global_sim import GlobalSimulator, Request
    sim = GlobalSimulator(nodes=10_000, services=100_000)
    sim.schedule(Request(1, 1, 99_999, 256))
    sim.inject_failure(2, 9999)
    sim.schedule(Request(3, 2, 99_999, 128))
    stats = sim.run(10)
    assert stats.completed == 1
    assert stats.dropped == 1
    assert stats.bytes_processed == 256

def test_forensics_event_integrity_and_timeline():
    from atlas.security import EvidenceLog, EventKind, SecurityEvent
    log = EvidenceLog([])
    log.append(SecurityEvent.create(2, EventKind.AUTH, "alice", "login", "svc", {"ip": "1.2.3.4"}))
    log.append(SecurityEvent.create(1, EventKind.FILE, "bob", "read", "/x", {}))
    assert [e.timestamp_ns for e in log.timeline()] == [1, 2]
    assert len(log.query(actor="alice")) == 1
    assert log.verify_integrity()

def test_sbom_and_build_provenance_are_deterministic():
    from atlas.packages import Artifact, BuildProvenance, SBOM
    sbom = SBOM()
    sbom.add("python", "3.12")
    sbom.add("z3-solver", "4.13")
    assert sbom.digest() == SBOM_with_same_content().digest()

def SBOM_with_same_content():
    from atlas.packages import SBOM
    result = SBOM()
    result.add("z3-solver", "4.13")
    result.add("python", "3.12")
    return result

def test_provenance_digest_changes_with_revision():
    from atlas.packages import Artifact, BuildProvenance
    artifact = Artifact("atlas.bin", "abc", 3)
    a = BuildProvenance("atlas-builder", "rev1", ("build",), (artifact,), ("py",))
    b = BuildProvenance("atlas-builder", "rev2", ("build",), (artifact,), ("py",))
    assert a.digest() != b.digest()
