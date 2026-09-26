from atlas.distributed import QuorumTracker
from atlas.observability import SLOTracker
from atlas.security import NonceReplayGuard


def test_quorum():
    q = QuorumTracker(["a", "b", "c"])
    assert not q.reached
    q.acknowledge("a")
    q.acknowledge("b")
    assert q.reached
    assert q.result().required == 2


def test_replay_guard():
    guard = NonceReplayGuard()
    assert guard.check("alice", 1).accepted
    assert not guard.check("alice", 1).accepted
    assert not guard.check("alice", 0).accepted
    assert guard.check("alice", 2).accepted


def test_slo():
    slo = SLOTracker(0.9)
    for _ in range(9):
        slo.observe(True)
    slo.observe(False)
    result = slo.result()
    assert result.availability == 0.9
    assert result.compliant


if __name__ == "__main__":
    test_quorum()
    test_replay_guard()
    test_slo()
    print("ATLAS twelfth-wave tests: PASS")
