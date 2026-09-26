from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable

from .model import Event

def sequence_id(events: Iterable[Event]) -> str:
    payload = json.dumps(
        [event.to_dict() for event in events],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:20]

class CorpusStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, events: Iterable[Event], metadata: dict | None = None) -> Path:
        events = tuple(events)
        key = sequence_id(events)
        target = self.root / f"{key}.json"
        data = {
            "id": key,
            "events": [e.to_dict() for e in events],
            "metadata": metadata or {},
        }
        target.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return target

    def ids(self) -> list[str]:
        return sorted(p.stem for p in self.root.glob("*.json"))

    def read(self, key: str) -> dict:
        return json.loads((self.root / f"{key}.json").read_text(encoding="utf-8"))

    def count(self) -> int:
        return len(self.ids())

__all__ = ["sequence_id", "CorpusStore"]
