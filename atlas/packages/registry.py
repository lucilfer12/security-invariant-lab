from __future__ import annotations

from dataclasses import dataclass, field
import hashlib

@dataclass(frozen=True)
class Package:
    name: str
    version: str
    dependencies: tuple[str, ...] = ()
    digest: str = ""

    def identity(self) -> str:
        return f"{self.name}@{self.version}"

@dataclass
class Registry:
    packages: dict[str, Package] = field(default_factory=dict)

    def publish(self, package: Package, content: bytes) -> Package:
        digest = hashlib.sha256(content).hexdigest()
        stored = Package(package.name, package.version, package.dependencies, digest)
        self.packages[stored.identity()] = stored
        return stored

    def resolve(self, name: str, version: str) -> Package:
        return self.packages[f"{name}@{version}"]

    def verify(self, package: Package, content: bytes) -> bool:
        return hashlib.sha256(content).hexdigest() == package.digest
