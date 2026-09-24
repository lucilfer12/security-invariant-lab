from __future__ import annotations

import unittest

from invariant_lab.core import Case, Engine, Invariant, InvariantResult, Event
from invariant_lab.core.minimize import minimize_trace


class SimpleInvariant(Invariant):
    name = "x-nonnegative"
    def check(self, state):
        return InvariantResult(state["x"] >= 0, f"x became negative: {state['x']}")


class Model:
    def fresh(self):
        return {"x": 0}
    def apply(self, state, event):
        state["x"] += event.params.get("delta", 0)
    def snapshot(self, state, label="state"):
        from invariant_lab.core.model import StateSnapshot
        return StateSnapshot(label, dict(state))


class CoreTests(unittest.TestCase):
    def test_engine_detects_violation(self):
        result = Engine(Model(), [SimpleInvariant()]).run_case(
            Case("negative", (Event("inc", {"delta": 1}), Event("dec", {"delta": -2})))
        )
        self.assertFalse(result.passed)
        self.assertIsNotNone(result.finding)
        self.assertEqual(len(result.finding.trace), 2)

    def test_minimizer_removes_irrelevant_events(self):
        events = [1, 2, 3, 4]
        minimized = minimize_trace(events, lambda xs: 4 in xs and 2 in xs)
        self.assertEqual(minimized, [2, 4])

    def test_event_serialization(self):
        self.assertEqual(Event("x", {"a": 1}).to_dict(), {"name": "x", "params": {"a": 1}})


if __name__ == "__main__":
    unittest.main()
