from __future__ import annotations

from dataclasses import dataclass

from invariant_lab.core import Case, Engine, Invariant, InvariantResult, Event


@dataclass
class VaultState:
    share_value: int = 100
    idle: int = 0
    child_available: int = 90
    payout: int = 0
    position_burned: bool = False

    def snapshot(self, label="state"):
        from invariant_lab.core.model import StateSnapshot
        return StateSnapshot(label, {
            "share_value": self.share_value,
            "idle": self.idle,
            "child_available": self.child_available,
            "payout": self.payout,
            "position_burned": self.position_burned,
        })


class VaultModel:
    def fresh(self):
        return VaultState()

    def snapshot(self, state, label="state"):
        return state.snapshot(label)

    def apply(self, s: VaultState, event: Event):
        if event.name == "prepare_withdraw":
            needed = max(s.share_value - s.idle, 0)
            if s.child_available + 10 < needed:
                return
            pulled = min(needed, s.child_available)
            s.child_available -= pulled
            s.idle += pulled
            s.payout = min(s.share_value, s.idle)
            # The vulnerable pattern: the position is settled because a boolean success flag
            # is modeled as unconditional even though payout may be short.
            s.position_burned = True


class FullPayoutInvariant(Invariant):
    name = "full-exit-must-not-burn-on-shortfall"
    description = "A full position must not be destroyed unless payout equals share value."

    def check(self, s: VaultState):
        violated = s.position_burned and s.payout < s.share_value
        return InvariantResult(
            not violated,
            message=f"Position burned with payout {s.payout} < share value {s.share_value}.",
            evidence={"payout": s.payout, "share_value": s.share_value},
        )


def main():
    case = Case("partial-payout-burn", (Event("prepare_withdraw"),))
    result = Engine(VaultModel(), [FullPayoutInvariant()]).run_case(case)
    print("DeFi payout invariant demo")
    print("--------------------------")
    print(f"passed: {result.passed}")
    if result.finding:
        print(result.finding.message)
        print("before:", result.finding.before.data)
        print("after:", result.finding.after.data)
    return result


if __name__ == "__main__":
    main()
