from __future__ import annotations

import random

from invariant_lab.core import (
    Case,
    Engine,
    Event,
    FuzzConfig,
    Invariant,
    InvariantResult,
    SequenceFuzzer,
    event_coverage,
)


class CounterModel:
    def fresh(self):
        return {"value": 0}

    def snapshot(self, state, label="state"):
        from invariant_lab.core.model import StateSnapshot
        return StateSnapshot(label, dict(state))

    def apply(self, state, event):
        state["value"] += event.params["delta"]


class NonNegative(Invariant):
    name = "counter-never-negative"

    def check(self, state):
        return InvariantResult(state["value"] >= 0, f"value={state['value']}")


def main():
    def factory(rng: random.Random) -> Event:
        return Event("adjust", {"delta": rng.choice([-2, -1, 1, 2])})

    fuzzer = SequenceFuzzer(factory, FuzzConfig(seed=2026, cases=20, max_length=8))
    cases = fuzzer.cases()
    results = Engine(CounterModel(), [NonNegative()]).run(cases)
    failed = next((r for r in results if not r.passed), None)
    print("Deterministic fuzz demo")
    print("-----------------------")
    print("cases:", len(results))
    print("failed:", failed.case.name if failed else "none")
    print("coverage:", event_coverage(case.events for case in cases))
    return failed


if __name__ == "__main__":
    main()
