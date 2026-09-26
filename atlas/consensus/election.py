from dataclasses import dataclass


@dataclass(frozen=True)
class Lease:
    leader_id: str
    term: int
    expires_at: int


class LeaseElection:
    """Deterministic lease-based leader election reference model."""

    def __init__(self, node_id: str, lease_ticks: int = 5):
        if lease_ticks <= 0:
            raise ValueError("lease_ticks must be positive")
        self.node_id = node_id
        self.lease_ticks = lease_ticks
        self.term = 0
        self.lease = None

    def acquire(self, term: int, now: int) -> Lease:
        if term < self.term:
            raise ValueError("term regression")
        self.term = term
        self.lease = Lease(self.node_id, term, now + self.lease_ticks)
        return self.lease

    def valid(self, now: int) -> bool:
        return self.lease is not None and now < self.lease.expires_at

    def renew(self, now: int) -> Lease:
        if not self.valid(now):
            raise RuntimeError("lease expired")
        self.lease = Lease(self.node_id, self.term, now + self.lease_ticks)
        return self.lease
