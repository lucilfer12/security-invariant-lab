from __future__ import annotations

import unittest

from invariant_lab.core import Event, event_coverage, compare_sequences


class AdvancedTests(unittest.TestCase):
    def test_event_coverage(self):
        cov = event_coverage([[Event("a"), Event("b")], [Event("a")]])
        self.assertEqual(cov.event_counts, {"a": 2, "b": 1})
        self.assertEqual(cov.total_events, 3)
        self.assertEqual(cov.unique_events, 2)

    def test_differential_comparison(self):
        events = [Event("x", {"n": 1}), Event("x", {"n": 2})]
        left = {"v": 0}
        right = {"v": 0}
        def a(s, e): s["v"] += e.params["n"]
        def b(s, e): s["v"] += e.params["n"] * (2 if e.params["n"] == 2 else 1)
        mismatches = compare_sequences(events, a, b, left, right)
        self.assertEqual(mismatches[0].step, 1)


if __name__ == "__main__":
    unittest.main()
