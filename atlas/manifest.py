from __future__ import annotations

from dataclasses import dataclass, asdict
import json
import platform
import sys

@dataclass(frozen=True)
class Manifest:
    name: str = "ATLAS"
    version: str = "0.2.0"
    python: str = sys.version.split()[0]
    platform: str = platform.platform()
    capabilities: tuple[str, ...] = ()

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2) + "\n"

def default_manifest() -> Manifest:
    caps = ("isa", "runtime", "policy", "capability", "distributed",
            "cas", "wal", "protocol", "silab", "identity", "consensus",
            "build", "simulation", "blockchain-vm", "ai-security",
            "compiler", "os", "cloud", "packages", "formal")
    return Manifest(capabilities=caps)
