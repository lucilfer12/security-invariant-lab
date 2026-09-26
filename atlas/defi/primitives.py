from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext
from statistics import median

getcontext().prec = 50

class EconomicError(ValueError):
    pass

@dataclass
class ConstantProductPool:
    reserve_x: Decimal
    reserve_y: Decimal
    fee_bps: int = 30

    def quote_exact_in(self, amount_in: Decimal) -> Decimal:
        if amount_in <= 0 or self.reserve_x <= 0 or self.reserve_y <= 0:
            raise EconomicError("invalid reserves or input")
        fee_multiplier = Decimal(10000 - self.fee_bps) / Decimal(10000)
        effective = amount_in * fee_multiplier
        return (effective * self.reserve_y) / (self.reserve_x + effective)

    def swap_x_for_y(self, amount_in: Decimal) -> Decimal:
        out = self.quote_exact_in(amount_in)
        self.reserve_x += amount_in
        self.reserve_y -= out
        if self.reserve_y <= 0:
            raise EconomicError("pool exhausted")
        return out

    def invariant(self) -> Decimal:
        return self.reserve_x * self.reserve_y
@dataclass
class LendingPosition:
    collateral: Decimal
    debt: Decimal

    def health(self, collateral_price: Decimal, liquidation_threshold: Decimal) -> Decimal:
        if self.debt <= 0:
            return Decimal("Infinity")
        return (self.collateral * collateral_price * liquidation_threshold) / self.debt

@dataclass
class MedianOracle:
    max_deviation_bps: int = 500

    def aggregate(self, prices: list[Decimal]) -> Decimal:
        if not prices or any(p <= 0 for p in prices):
            raise EconomicError("invalid oracle sample set")
        return Decimal(str(median(prices)))

    def safe(self, prices: list[Decimal]) -> tuple[Decimal, bool]:
        price = self.aggregate(prices)
        spread = max(prices) - min(prices)
        deviation_bps = spread * Decimal(10000) / price
        return price, deviation_bps <= self.max_deviation_bps

def liquidation_amount(position: LendingPosition, collateral_price: Decimal,
                        threshold: Decimal, close_factor: Decimal) -> Decimal:
    health = position.health(collateral_price, threshold)
    if health >= 1:
        return Decimal("0")
    if not 0 < close_factor <= 1:
        raise EconomicError("invalid close factor")
    return min(position.debt * close_factor, position.debt)
