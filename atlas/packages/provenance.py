from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

@dataclass(frozen=True)
class Artifact:
    path: str
    digest: str
    size: int

@dataclass(frozen=True)
class BuildProvenance:
    builder: str
    source_revision: str
    command: tuple[str, ...]
    artifacts: tuple[Artifact, ...]
    dependencies: tuple[str, ...]

    def canonical(self) -> bytes:
        return json.dumps({
            "builder": self.builder,
            "source_revision": self.source_revision,
            "command": list(self.command),
            "artifacts": [a.__dict__ for a in self.artifacts],
            "dependencies": list(self.dependencies),
        }, sort_keys=True, separators=(",", ":")).encode()

    def digest(self) -> str:
        return hashlib.sha256(self.canonical()).hexdigest()

class SBOM:
    def __init__(self):
        self.components: dict[str, str] = {}

    def add(self, name: str, version: str) -> None:
        if not name or not version:
            raise ValueError("component name/version required")
        self.components[name] = version

    def document(self) -> dict:
        return {
            "format": "ATLAS-SBOM-1",
            "components": [
                {"name": name, "version": version}
                for name, version in sorted(self.components.items())
            ],
        }

    def digest(self) -> str:
        raw = json.dumps(self.document(), sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()
