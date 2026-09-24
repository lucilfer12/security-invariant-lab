from __future__ import annotations

import unittest

from examples.defi_payout_shortfall import FullPayoutInvariant, VaultModel
from examples.pqc_seed_binding import derive_seed
from examples.replay_nonce_reset import GasKeyModel, NoReplay
from invariant_lab.core import Case, Engine, Event


class ExampleTests(unittest.TestCase):
    def test_replay_reset_is_detected(self):
        case = Case("replay", (
            Event("execute_delegate", {"nonce": 1}),
            Event("delete_key"),
            Event("readd_key", {"block": 150}),
        ))
        result = Engine(GasKeyModel(), [NoReplay()]).run_case(case)
        self.assertFalse(result.passed)
        self.assertIn("replayable", result.finding.message.lower())

    def test_pqc_binding_changes_seed(self):
        a = derive_seed("same mnemonic", "acct-A", "adapter")
        b = derive_seed("same mnemonic", "acct-B", "adapter")
        self.assertNotEqual(a, b)
        c = derive_seed("same mnemonic", "acct-A", "bridge")
        d = derive_seed("same mnemonic", "acct-B", "bridge")
        self.assertEqual(c, d)

    def test_payout_shortfall_detected(self):
        result = Engine(VaultModel(), [FullPayoutInvariant()]).run_case(
            Case("shortfall", (Event("prepare_withdraw"),))
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.finding.metadata["payout"], 90)


if __name__ == "__main__":
    unittest.main()
