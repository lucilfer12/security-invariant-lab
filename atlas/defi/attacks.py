from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from .primitives import ConstantProductPool, MedianOracle, LendingPosition

@dataclass(frozen=True)
class OracleAttackScenario:
    honest_price: Decimal
    manipulated_price: Decimal
    samples: tuple[Decimal, ...]

@dataclass(frozen=True)
class FlashLoanAttackResult:
    borrowed: Decimal
    extracted: Decimal
    net_profit: Decimal
    pool_invariant_before: Decimal
    pool_invariant_after: Decimal

def sandwich_simulation(pool: ConstantProductPool, victim_in: Decimal,
                        attacker_in: Decimal) -> FlashLoanAttackResult:
    before = pool.invariant()
    attack_out = pool.swap_x_for_y(attacker_in)
    victim_out = pool.swap_x_for_y(victim_in)
    unwind = pool.reserve_y if attack_out > pool.reserve_y else attack_out
    net = unwind - attacker_in
    return FlashLoanAttackResult(attacker_in, victim_out, net, before, pool.invariant())

def oracle_manipulation_risk(oracle: MedianOracle, scenario: OracleAttackScenario) -> dict:
    price, safe = oracle.safe(list(scenario.samples))
    distortion = abs(price - scenario.honest_price) / scenario.honest_price
    return {
        "aggregated_price": price,
        "safe": safe,
        "relative_distortion": distortion,
        "manipulated_sample_seen": scenario.manipulated_price in scenario.samples,
    }

def liquidation_risk(position: LendingPosition, collateral_price: Decimal,
                      threshold: Decimal) -> dict:
    health = position.health(collateral_price, threshold)
    return {"health": health, "liquidatable": health < 1}
