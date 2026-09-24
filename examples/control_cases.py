from __future__ import annotations

import hashlib
from dataclasses import dataclass

from invariant_lab.core import Case, Engine, Event, Invariant, InvariantResult


class FixedReplayModel:
    def fresh(self):
        return {"nonce": 0, "executed": set(), "active": True}

    def snapshot(self, state, label="state"):
        from invariant_lab.core.model import StateSnapshot
        return StateSnapshot(label, {"nonce": state["nonce"], "executed": sorted(state["executed"]), "active": state["active"]})

    def apply(self, s, e):
        if e.name == "execute_delegate":
            n = e.params["nonce"]
            if s["active"] and n > s["nonce"]:
                s["nonce"] = n
                s["executed"].add(n)
        elif e.name == "delete_key":
            s["active"] = False
        elif e.name == "readd_key":
            s["active"] = True
            s["nonce"] = 149_000_000  # block-height-derived initialization


class ReplayInvariant(Invariant):
    name = "executed-nonce-remains-invalid"
    def check(self, s):
        replayable = [n for n in s["executed"] if n > s["nonce"]]
        return InvariantResult(not replayable, f"replayable={replayable}")


@dataclass
class FixedVault:
    share_value: int = 100
    idle: int = 0
    child_available: int = 90
    burned: bool = False
    payout: int = 0


class FixedVaultModel:
    def fresh(self):
        return FixedVault()

    def snapshot(self, s, label="state"):
        from invariant_lab.core.model import StateSnapshot
        return StateSnapshot(label, vars(s).copy())

    def apply(self, s, e):
        if e.name == "prepare_withdraw":
            needed = max(s.share_value - s.idle, 0)
            if s.child_available < needed:
                return
            s.idle += needed
            s.child_available -= needed
            if s.idle >= s.share_value:
                s.payout = s.share_value
                s.burned = True


class NoShortfallBurn(Invariant):
    name = "fixed-vault-no-shortfall-burn"
    def check(self, s):
        return InvariantResult(not (s.burned and s.payout < s.share_value), "shortfall burn")


def main():
    replay = Engine(FixedReplayModel(), [ReplayInvariant()]).run_case(
        Case("fixed-replay-control", (
            Event("execute_delegate", {"nonce": 1}),
            Event("delete_key"),
            Event("readd_key"),
        ))
    )
    vault = Engine(FixedVaultModel(), [NoShortfallBurn()]).run_case(
        Case("fixed-payout-control", (Event("prepare_withdraw"),))
    )
    print("Control cases")
    print("-------------")
    print("replay protection:", replay.passed)
    print("payout shortfall:", vault.passed)


if __name__ == "__main__":
    main()
