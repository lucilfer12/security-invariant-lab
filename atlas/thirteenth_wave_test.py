from atlas.distributed import GCounter, LWWRegister, Member, MemberState, Membership
from atlas.network import KeyedRateLimiter


def test_membership_ordering():
    table = Membership()
    assert table.upsert(Member("n1", 1))
    assert not table.upsert(Member("n1", 0, MemberState.DEAD))
    assert table.upsert(Member("n1", 2, MemberState.SUSPECT))
    assert table.upsert(Member("n1", 3, MemberState.DEAD))
    assert table.get("n1").state == MemberState.DEAD


def test_crdt_merge_is_monotonic():
    left = GCounter("a")
    right = GCounter("b")
    left.increment(2)
    right.increment(3)
    left.merge(right)
    right.merge(left)
    assert left.value == right.value == 5
    assert left.state() == {"a": 2, "b": 3}

    a = LWWRegister("a")
    b = LWWRegister("b")
    a.assign("old", 1)
    b.assign("new", 2)
    a.merge(b)
    b.merge(a)
    assert a.value == b.value == "new"


def test_rate_limit():
    limiter = KeyedRateLimiter(capacity=2, refill_per_tick=1)
    assert limiter.allow("client", tick=0).allowed
    assert limiter.allow("client", tick=0).allowed
    denied = limiter.allow("client", tick=0)
    assert not denied.allowed
    assert denied.retry_after == 1
    assert limiter.allow("client", tick=1).allowed


if __name__ == "__main__":
    test_membership_ordering()
    test_crdt_merge_is_monotonic()
    test_rate_limit()
    print("ATLAS thirteenth-wave tests: PASS")
