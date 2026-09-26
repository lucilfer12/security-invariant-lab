from __future__ import annotations

from .ai import ModelRegistry
from .blockchain import Chain
from .database import MVCCStore
from .distributed import ConsistentHashRing, LamportClock
from .manifest import default_manifest
from .observability import Tracer
from .security import Policy
from .storage import CAS, WAL

class AtlasPlatform:
    """Unified composition root; subsystems remain independently testable."""

    def __init__(self, data_dir: str = ".atlas"):
        from pathlib import Path
        root = Path(data_dir)
        self.manifest = default_manifest()
        self.store = MVCCStore()
        self.chain = Chain()
        self.ring = ConsistentHashRing()
        self.clock = LamportClock()
        self.models = ModelRegistry()
        self.tracer = Tracer()
        self.cas = CAS(root / "cas")
        self.wal = WAL(root / "wal.log")
        self.policy: Policy | None = None

    def health(self) -> dict:
        return {"name": self.manifest.name, "version": self.manifest.version,
                "chain_height": len(self.chain.blocks), "clock": self.clock.value,
                "models": len(self.models.models), "wal_records": len(self.wal.recover())}
