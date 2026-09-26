from __future__ import annotations

import re
from pathlib import Path

from .types import CandidateInvariant, ContractRecord, ScanResult

RULES = (
    (("totalSupply", "balances"), "supply_conservation", "sum(balances) == totalSupply",
     "Balance mapping and total supply suggest a conservation property.", "medium"),
    (("totalDeposits", "balances"), "deposit_conservation", "sum(balances) == totalDeposits",
     "Deposit aggregate and per-user balances suggest accounting conservation.", "medium"),
    (("totalAssets", "totalLiabilities"), "solvency_floor", "totalAssets >= totalLiabilities",
     "Asset/liability aggregates suggest a solvency floor.", "medium"),
    (("nonce",), "nonce_monotonicity", "nonce_after >= nonce_before",
     "Nonce state suggests replay-protection monotonicity.", "high"),
    (("owner", "admin"), "admin_authorization", "unauthorized_caller => privileged_state_unchanged",
     "Owner/admin state suggests an authorization invariant.", "medium"),
    (("implementation", "upgrade"), "upgrade_authorization",
     "unauthorized_caller => implementation_after == implementation_before",
     "Upgrade-related identifiers suggest an upgrade authorization property.", "medium"),
    (("paused",), "paused_mutation", "paused => sensitive_mutations_are_disabled",
     "Pause state suggests a lifecycle safety property.", "medium"),
    (("collateral", "debt"), "collateralization", "collateral_value >= debt",
     "Collateral and debt identifiers suggest a lending solvency property.", "low"),
    (("price", "oracle"), "oracle_sanity", "price > 0 && price_is_fresh",
     "Oracle/price logic suggests a freshness and positivity property.", "low"),
)

def _identifiers(contract: ContractRecord) -> set[str]:
    text = " ".join(contract.state_variables)
    for fn in contract.functions:
        text += " " + fn.name + " " + fn.body
    return set(re.findall(r"[A-Za-z_]\w*", text))

def candidates_for_contract(contract: ContractRecord) -> list[CandidateInvariant]:
    ids = _identifiers(contract)
    candidates: list[CandidateInvariant] = []
    for required, name, expression, rationale, confidence in RULES:
        if set(required) <= ids:
            candidates.append(CandidateInvariant(
                name=f"{contract.name}:{name}",
                expression=expression,
                rationale=rationale,
                source=contract.file,
                confidence=confidence,
            ))
    if any("withdraw" in f.name.lower() for f in contract.functions):
        candidates.append(CandidateInvariant(
            name=f"{contract.name}:withdraw_not_above_balance",
            expression="withdraw_amount <= caller_available_balance",
            rationale="Withdraw-like entrypoints should not reduce an account below its available balance.",
            source=contract.file,
            confidence="low",
        ))
    if any("mint" in f.name.lower() for f in contract.functions) and "totalSupply" in ids:
        candidates.append(CandidateInvariant(
            name=f"{contract.name}:mint_supply_consistency",
            expression="totalSupply_after == totalSupply_before + minted_amount",
            rationale="Mint entrypoints imply a supply/accounting relationship.",
            source=contract.file,
            confidence="low",
        ))
    return candidates

def discover_invariants(result: ScanResult) -> list[CandidateInvariant]:
    found: list[CandidateInvariant] = []
    for contract in result.contracts:
        found.extend(candidates_for_contract(contract))
    unique: dict[str, CandidateInvariant] = {x.name: x for x in found}
    return list(unique.values())
def render_invariant_markdown(candidates: list[CandidateInvariant]) -> str:
    lines = [
        "# Candidate Security Properties",
        "",
        "These are hypotheses derived from source structure. They are not proofs or vulnerability verdicts.",
        "",
        "| Name | Expression | Confidence | Source |",
        "|---|---|---|---|",
    ]
    for item in candidates:
        lines.append("| {} | {} | {} | {} |".format(
            item.name, item.expression, item.confidence, Path(item.source).name
        ))
    return "\n".join(lines) + "\n"

__all__ = ["discover_invariants", "candidates_for_contract", "render_invariant_markdown"]
def property_statuses(candidates: list[CandidateInvariant]) -> list[dict]:
    return [
        {
            "name": item.name,
            "expression": item.expression,
            "status": "UNVERIFIED",
            "confidence": item.confidence,
            "rationale": item.rationale,
        }
        for item in candidates
    ]
