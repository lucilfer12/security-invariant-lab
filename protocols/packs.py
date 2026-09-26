from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_CATALOG = Path(__file__).with_name("catalog.json")

class ProtocolPackRegistry:
    def __init__(self, catalog: str | Path = DEFAULT_CATALOG):
        self.catalog = Path(catalog)
        data = json.loads(self.catalog.read_text(encoding="utf-8"))
        self.packs: dict[str, dict[str, Any]] = {
            item["id"]: item for item in data.get("packs", [])
        }

    def ids(self) -> list[str]:
        return sorted(self.packs)

    def get(self, pack_id: str) -> dict[str, Any]:
        return self.packs[pack_id]

    def match(self, identifiers: set[str]) -> list[dict[str, Any]]:
        matched = []
        for pack in self.packs.values():
            signals = set(pack.get("signals", []))
            if identifiers & signals:
                matched.append(pack)
        return sorted(matched, key=lambda x: x["id"])

def load_default_registry() -> ProtocolPackRegistry:
    return ProtocolPackRegistry(DEFAULT_CATALOG)

__all__ = ["ProtocolPackRegistry", "load_default_registry"]
