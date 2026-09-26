from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import json

@dataclass(frozen=True)
class ObjectMeta:
    key: str
    digest: str
    size: int
    version: int
    metadata: dict[str, str]

class ObjectStore:
    """Content-addressed object store with immutable versions and metadata."""
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._versions: dict[str, list[ObjectMeta]] = {}

    def put(self, key: str, data: bytes, metadata: dict[str, str] | None = None) -> ObjectMeta:
        if not key:
            raise ValueError("key cannot be empty")
        digest = hashlib.sha256(data).hexdigest()
        version = len(self._versions.get(key, ())) + 1
        path = self.root / digest
        if not path.exists():
            path.write_bytes(data)
        meta = ObjectMeta(key, digest, len(data), version, dict(metadata or {}))
        self._versions.setdefault(key, []).append(meta)
        (self.root / f"{key.replace('/', '_')}.index.json").write_text(
            json.dumps([m.__dict__ for m in self._versions[key]], sort_keys=True),
            encoding="utf-8",
        )
        return meta

    def get(self, key: str, version: int | None = None) -> bytes:
        versions = self._versions.get(key)
        if not versions:
            raise KeyError(key)
        meta = versions[-1] if version is None else versions[version - 1]
        data = (self.root / meta.digest).read_bytes()
        if hashlib.sha256(data).hexdigest() != meta.digest:
            raise IOError("object integrity failure")
        return data

    def list_versions(self, key: str) -> tuple[ObjectMeta, ...]:
        return tuple(self._versions.get(key, ()))
class ReedSolomonShard:
    """Simple XOR parity for a two-data-shard + one-parity erasure profile."""
    width = 2

    @staticmethod
    def encode(data: bytes) -> tuple[bytes, bytes, bytes]:
        midpoint = (len(data) + 1) // 2
        left, right = data[:midpoint], data[midpoint:]
        right += b"\x00" * (len(left) - len(right))
        parity = bytes(a ^ b for a, b in zip(left, right))
        return left, right, parity

    @classmethod
    def recover(cls, shards: tuple[bytes | None, bytes | None, bytes | None]) -> bytes:
        left, right, parity = shards
        missing = sum(s is None for s in shards)
        if missing > 1:
            raise ValueError("profile cannot recover two or more missing shards")
        if left is None:
            if right is None or parity is None:
                raise ValueError("insufficient shards")
            left = bytes(a ^ b for a, b in zip(right, parity))
        elif right is None:
            right = bytes(a ^ b for a, b in zip(left, parity or b""))
        elif parity is None:
            parity = bytes(a ^ b for a, b in zip(left, right))
        return (left + right).rstrip(b"\x00")
