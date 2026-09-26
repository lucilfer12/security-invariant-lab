from __future__ import annotations

import importlib.util
import shutil

def manifest() -> dict:
    return {
        "platform": "Security Invariant Lab",
        "version": "0.5.0",
        "implemented": [
            "deterministic invariant engine",
            "stateful fuzzing",
            "differential testing",
            "failure minimization",
            "evidence bundles",
            "Solidity intelligence",
            "attack-surface graph",
            "candidate invariant discovery",
            "taint hypotheses",
            "mutation candidates",
            "threat modeling",
            "HTML Markdown SARIF JUnit exports",
            "Gemini copilot",
            "Foundry adapter",
        ],
        "optional_runtime": {
            "forge": bool(shutil.which("forge")) or (shutil.which("forge") is not None),
            "anvil": bool(shutil.which("anvil")),
            "z3": importlib.util.find_spec("z3") is not None,
            "gemini_api_key": bool(__import__("os").getenv("GEMINI_API_KEY")),
        },
        "extension_points": [
            "symbolic execution",
            "SMT solver backends",
            "distributed workers",
            "IDE and GitHub integrations",
            "additional language adapters",
        ],
    }
