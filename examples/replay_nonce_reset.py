from __future__ import annotations

from dataclasses import dataclass, field

from invariant_lab.core import Case, Engine, Invariant, InvariantResult, Event


@dataclass
class GasKeyState:
    nonce: int = 0
    executed: set[int] = field(default_factory=set)
    active: bool = True
    current_block: int = 100

    def snapshot(self, label="state"):
        from invariant_lab.core.model import StateSnapshot
        return StateSnapshot(label, {
            "nonce": self.nonce,
            "executed": sorted(self.executed),
            "active": self.active,
            "current_block": self.current_block,
        })


class GasKeyModel:
    def fresh(self):
        return GasKeyState()

    def snapshot(self, state, label="state"):
        return state.snapshot(label)

    def apply(self, s: GasKeyState, event: Event):
        if event.name == "execute_delegate":
            n = int(event.params["nonce"])
            if n > s.nonce and s.active:
                s.nonce = n
                s.executed.add(n)
        elif event.name == "delete_key":
            s.active = False
        elif event.name == "readd_key":
            s.active = True
            s.nonce = 0  # intentionally vulnerable model
            s.current_block = int(event.params.get("block", s.current_block))


class NoReplay(Invariant):
    name = "delegate-actions-are-not-replayable"
    description = "An already executed nonce must not become valid again after key lifecycle changes."

    def check(self, s: GasKeyState):
        replayable = [n for n in s.executed if n > s.nonce]
        return InvariantResult(
            not replayable,
            message=f"Previously executed nonce(s) became replayable: {replayable}",
            evidence={"replayable_nonces": replayable},
        )


def main():
    case = Case("delete-readd-replay", (
        Event("execute_delegate", {"nonce": 1}),
        Event("delete_key"),
        Event("readd_key", {"block": 150}),
    ))
    result = Engine(GasKeyModel(), [NoReplay()]).run_case(case)
    print("Replay lifecycle demo")
    print("---------------------")
    print(f"passed: {result.passed}")
    if result.finding:
        print(f"invariant: {result.finding.invariant}")
        print(result.finding.message)
        print("trace:", [e.name for e in result.finding.trace])
    return result


if __name__ == "__main__":
    main()
