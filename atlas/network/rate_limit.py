from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after: int


class TokenBucket:
    """Deterministic integer token bucket for protocol admission control."""

    def __init__(self, capacity: int, refill_per_tick: int):
        if capacity <= 0 or refill_per_tick < 0:
            raise ValueError("invalid token bucket parameters")
        self.capacity = capacity
        self.refill_per_tick = refill_per_tick
        self.tokens = capacity
        self.last_tick = 0

    def _refill(self, tick: int):
        if tick < self.last_tick:
            raise ValueError("tick cannot move backwards")
        self.tokens = min(
            self.capacity,
            self.tokens + (tick - self.last_tick) * self.refill_per_tick,
        )
        self.last_tick = tick

    def allow(self, cost: int = 1, tick: int = 0) -> RateLimitDecision:
        if cost <= 0:
            raise ValueError("cost must be positive")
        self._refill(tick)
        if self.tokens >= cost:
            self.tokens -= cost
            return RateLimitDecision(True, self.tokens, 0)
        deficit = cost - self.tokens
        retry = 0 if self.refill_per_tick == 0 else (deficit + self.refill_per_tick - 1) // self.refill_per_tick
        return RateLimitDecision(False, self.tokens, retry)


class KeyedRateLimiter:
    def __init__(self, capacity: int, refill_per_tick: int):
        self.capacity = capacity
        self.refill_per_tick = refill_per_tick
        self._buckets = {}

    def allow(self, key: str, cost: int = 1, tick: int = 0) -> RateLimitDecision:
        bucket = self._buckets.setdefault(
            key, TokenBucket(self.capacity, self.refill_per_tick)
        )
        return bucket.allow(cost, tick)
