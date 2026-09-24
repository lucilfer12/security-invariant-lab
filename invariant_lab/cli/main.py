from __future__ import annotations

import argparse
import runpy
from pathlib import Path

from invariant_lab.core.engine import Engine
from invariant_lab.core.evidence import write_evidence
from invariant_lab.core.minimize import minimize_trace


def _demo(name: str) -> int:
    module = f"examples.{name}"
    runpy.run_module(module, run_name="__main__")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="silab", description="Security Invariant Lab")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run bundled demonstrations")
    demo.add_argument("name", choices=["all", "replay", "pqc", "defi"])

    run = sub.add_parser("run", help="execute a Python case module with a main entry point")
    run.add_argument("script", type=Path)

    args = parser.parse_args()
    if args.command == "demo":
        names = ["replay_nonce_reset", "pqc_seed_binding", "defi_payout_shortfall"] if args.name == "all" else {
            "replay": "replay_nonce_reset",
            "pqc": "pqc_seed_binding",
            "defi": "defi_payout_shortfall",
        }[args.name]
        if isinstance(names, list):
            for item in names:
                _demo(item)
        else:
            _demo(names)
        return 0

    if args.command == "run":
        namespace = runpy.run_path(str(args.script), run_name="__main__")
        return int(namespace.get("EXIT_CODE", 0))

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
