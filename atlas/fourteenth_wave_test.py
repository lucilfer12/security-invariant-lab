from atlas.consensus import LeaseElection
from atlas.distributed import PhiFailureDetector


def test_lease_election():
    election = LeaseElection("leader", lease_ticks=3)
    lease = election.acquire(2, 10)
    assert lease.expires_at == 13
    assert election.valid(12)
    assert not election.valid(13)
    try:
        election.renew(13)
    except RuntimeError:
        pass
    else:
        raise AssertionError("expired lease renewed")


def test_failure_detector():
    detector = PhiFailureDetector(threshold=2)
    detector.heartbeat("n1")
    assert not detector.tick("n1").suspected
    assert detector.tick("n1").suspected
    detector.heartbeat("n1")
    assert not detector.status("n1").suspected


if __name__ == "__main__":
    test_lease_election()
    test_failure_detector()
    print("ATLAS fourteenth-wave tests: PASS")
