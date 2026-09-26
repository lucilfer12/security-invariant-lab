from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ArtifactRecord:
    contract: str
    file: str
    abi_entries: int
    functions: int
    selectors: dict[str, str]
    storage_slots: int



def inventory_artifacts(root: str | Path) -> list[ArtifactRecord]:
    root = Path(root)
    out = []
    for path in root.rglob("*.json"):
        if "out" not in path.parts:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        abi = data.get("abi")
        if not isinstance(abi, list) or "bytecode" not in data:
            continue
        selectors = data.get("methodIdentifiers", {})
        storage = data.get("storageLayout", {}).get("storage", [])
        out.append(ArtifactRecord(
            contract=path.stem,
            file=str(path),
            abi_entries=len(abi),
            functions=sum(1 for x in abi if isinstance(x, dict) and x.get("type") == "function"),
            selectors=dict(selectors) if isinstance(selectors, dict) else {},
            storage_slots=len(storage) if isinstance(storage, list) else 0,
        ))
    return sorted(out, key=lambda x: (x.contract, x.file))

def artifact_report(root: str | Path) -> list[dict]:
    return [x.__dict__ for x in inventory_artifacts(root)]
