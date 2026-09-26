from __future__ import annotations

import json
import unittest
from pathlib import Path
import tempfile

from invariant_lab.core import Event, Engine, Invariant, InvariantResult, AdaptiveConfig, AdaptiveSequenceFuzzer
from invariant_lab.platform.baseline import compare_scans
from invariant_lab.platform.invariants import discover_invariants
from invariant_lab.platform.pipeline import scan_project
from invariant_lab.platform.smt import VerificationStatus, prove
from invariant_lab.platform.scanner import SolidityScanner

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "targets" / "bridge-lab"

class PlatformTests(unittest.TestCase):
    def test_scan_bridge_surface(self):
        result, out = scan_project(BRIDGE, ROOT / ".silab" / "test-platform")
        self.assertGreaterEqual(result.metrics["contracts"], 4)
        self.assertGreaterEqual(result.metrics["candidate_invariants"], 2)
        self.assertTrue((out / "report.html").exists())
        self.assertTrue((out / "report.sarif.json").exists())
    def test_replay_property_is_discovered(self):
        result = SolidityScanner(BRIDGE).scan()
        props = discover_invariants(result)
        self.assertTrue(any(p.name.endswith("message_replay") for p in props))

    def test_baseline_diff(self):
        baseline = {"findings": [{"id": "A"}], "root": "old"}
        current = {"findings": [{"id": "B"}], "root": "new"}
        diff = compare_scans(baseline, current)
        self.assertEqual(diff["introduced"], ["B"])
        self.assertEqual(diff["resolved"], ["A"])

    def test_smt_counterexample(self):
        from z3 import Int
        x = Int("x")
        result = prove(x >= 0, [x == -1])
        self.assertEqual(result.status, VerificationStatus.VIOLATED)
        self.assertEqual(result.model["x"], -1)

    def test_adaptive_fuzzer_is_deterministic(self):
        def factory(rng):
            return Event("set", {"value": rng.randint(0, 10)})
        a = AdaptiveSequenceFuzzer(factory, AdaptiveConfig(seed=7, cases=20)).cases()
        b = AdaptiveSequenceFuzzer(factory, AdaptiveConfig(seed=7, cases=20)).cases()
        self.assertEqual([c.events for c in a], [c.events for c in b])

if __name__ == "__main__":
    unittest.main()
