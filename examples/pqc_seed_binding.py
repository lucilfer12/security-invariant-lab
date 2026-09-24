from __future__ import annotations

import hashlib
from dataclasses import dataclass

from invariant_lab.core import Case, Engine, Invariant, InvariantResult, Event


@dataclass
class PQCState:
    mnemonic: str
    address: str = ""
    mode: str = "bridge"

    def snapshot(self, label="state"):
        from invariant_lab.core.model import StateSnapshot
        seed = derive_seed(self.mnemonic, self.address, self.mode)
        return StateSnapshot(label, {"address": self.address, "mode": self.mode, "seed": seed.hex()})


def derive_seed(mnemonic: str, address: str, mode: str) -> bytes:
    if mode == "adapter":
        material = f"qorechain:pqc:v1|{address}|{mnemonic}".encode()
    else:
        material = mnemonic.encode()
    return hashlib.shake_256(material).digest(32)


class SameMnemonicRequiresBinding(Invariant):
    name = "pqc-seed-must-be-account-bound"
    description = "Different account identifiers should not derive the same PQC seed from one mnemonic."

    def check(self, s: PQCState):
        # Compare two synthetic account identities under the selected derivation mode.
        a = derive_seed(s.mnemonic, "acct-A", s.mode)
        b = derive_seed(s.mnemonic, "acct-B", s.mode)
        same = a == b
        return InvariantResult(
            not same,
            message="Distinct accounts derived an identical PQC seed.",
            evidence={"account_a_seed": a.hex(), "account_b_seed": b.hex(), "mode": s.mode},
        )


def main():
    bridge = Case("bridge-mode", (Event("set_mode", {"mode": "bridge"}),))
    # The model is kept intentionally tiny; the invariant directly exercises the derivation boundary.
    class Model:
        def fresh(self):
            return PQCState("abandon ability able about above absent absorb abstract absurd abuse access accident")
        def apply(self, s, event):
            if event.name == "set_mode":
                s.mode = event.params["mode"]
        def snapshot(self, s, label="state"):
            return s.snapshot(label)

    result = Engine(Model(), [SameMnemonicRequiresBinding()]).run_case(bridge)
    print("PQC account-binding demo")
    print("------------------------")
    print(f"passed: {result.passed}")
    if result.finding:
        print(result.finding.message)
        print("mode:", result.finding.metadata.get("mode"))
    return result


if __name__ == "__main__":
    main()
