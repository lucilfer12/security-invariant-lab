from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

from invariant_lab.core.minimize import minimize_trace
from invariant_lab.platform.ai import ai_report
from invariant_lab.platform.graphs import build_graph, to_dot
from invariant_lab.platform.invariants import discover_invariants, render_invariant_markdown
from invariant_lab.platform.mutation import suggest_mutations
from invariant_lab.platform.pipeline import forge_test, scan_project
from invariant_lab.platform.replay import load_bundle
from invariant_lab.platform.scanner import SolidityScanner
from invariant_lab.platform.server import serve

def _demo(name: str) -> int:
    runpy.run_module(f"examples.{name}", run_name="__main__")
    return 0

def _scan_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", type=Path)
    parser.add_argument("--out", default=".silab")

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="silab",
        description="Security Invariant Lab — executable security research platform",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="run bundled local demonstrations")
    demo.add_argument("name", choices=["all", "replay", "pqc", "defi"])

    run = sub.add_parser("run", help="execute a Python case module")
    run.add_argument("script", type=Path)

    scan = sub.add_parser("scan", help="analyze Solidity and generate evidence/report artifacts")
    _scan_args(scan)

    graph = sub.add_parser("graph", help="print the security graph as DOT")
    _scan_args(graph)

    inv = sub.add_parser("invariants", help="discover candidate security properties")
    _scan_args(inv)

    mut = sub.add_parser("mutations", help="list source-level mutation candidates")
    mut.add_argument("path", type=Path)

    forge = sub.add_parser("forge-test", help="run authorized local Foundry tests")
    forge.add_argument("path", type=Path)
    forge.add_argument("--verbose", type=int, default=3)

    ai = sub.add_parser("ai", help="ask Gemini to analyze a local scan snapshot")
    _scan_args(ai)

    reproduce = sub.add_parser("reproduce", help="validate a reproducible SIL bundle")
    reproduce.add_argument("bundle", type=Path)

    dash = sub.add_parser("dashboard", help="serve the generated report locally")
    dash.add_argument("--dir", default=".silab")
    dash.add_argument("--host", default="127.0.0.1")
    dash.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    if args.command == "demo":
        names = ["replay_nonce_reset", "pqc_seed_binding", "defi_payout_shortfall"] if args.name == "all" else {
            "replay": "replay_nonce_reset", "pqc": "pqc_seed_binding",
            "defi": "defi_payout_shortfall",
        }[args.name]
        for item in names if isinstance(names, list) else [names]:
            _demo(item)
        return 0

    if args.command == "run":
        namespace = runpy.run_path(str(args.script), run_name="__main__")
        return int(namespace.get("EXIT_CODE", 0))

    if args.command == "scan":
        result, out = scan_project(args.path, args.out)
        print(json.dumps({"out": str(out.resolve()), "metrics": result.metrics}, indent=2))
        return 0

    if args.command == "graph":
        result, _ = scan_project(args.path, args.out)
        print(to_dot(build_graph(result)), end="")
        return 0

    if args.command == "invariants":
        result, _ = scan_project(args.path, args.out)
        print(render_invariant_markdown(discover_invariants(result)))
        return 0
    if args.command == "mutations":
        scanner = SolidityScanner(args.path)
        mutants = [m for f in scanner.files() for m in suggest_mutations(f)]
        print(json.dumps([m.__dict__ for m in mutants], indent=2))
        return 0

    if args.command == "forge-test":
        result = forge_test(args.path)
        print(json.dumps(result, indent=2, default=str))
        return 0 if result.get("returncode") == 0 else 1

    if args.command == "ai":
        result, out = scan_project(args.path, args.out)
        payload = ai_report(result.to_dict())
        target = out / "ai.json"
        target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 0 if "error" not in payload else 1

    if args.command == "reproduce":
        bundle = load_bundle(args.bundle)
        print(json.dumps({
            "bundle_id": bundle["bundle_id"],
            "schema_version": bundle["meta"].get("schema_version"),
            "target": bundle.get("target"),
            "status": "VALID_BUNDLE",
        }, indent=2))
        return 0

    if args.command == "dashboard":
        serve(args.dir, args.host, args.port)
        return 0

    return 1

if __name__ == "__main__":
    raise SystemExit(main())
