from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class FindingRecord:
    id: str
    kind: str
    title: str
    severity: str
    confidence: str
    file: str
    line: int
    evidence: str
    recommendation: str
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class FunctionRecord:
    name: str
    visibility: str
    modifiers: tuple[str, ...]
    payable: bool
    mutating: bool
    line: int
    signature: str
    body: str
    calls: tuple[str, ...] = ()@dataclass(frozen=True)
class ContractRecord:
    name: str
    file: str
    line: int
    bases: tuple[str, ...]
    functions: tuple[FunctionRecord, ...]
    state_variables: tuple[str, ...]
    events: tuple[str, ...]
    imports: tuple[str, ...]

@dataclass(frozen=True)
class CandidateInvariant:
    name: str
    expression: str
    rationale: str
    source: str
    confidence: str

@dataclass(frozen=True)
class AttackEdge:
    source: str
    target: str
    kind: str
    evidence: str

@dataclass(frozen=True)
class AttackSurface:
    contracts: tuple[ContractRecord, ...]
    privileged_functions: tuple[str, ...]
    external_entrypoints: tuple[str, ...]
    external_calls: tuple[str, ...]
    delegatecalls: tuple[str, ...]
    low_level_calls: tuple[str, ...]@dataclass
class ScanResult:
    root: str
    contracts: list[ContractRecord] = field(default_factory=list)
    findings: list[FindingRecord] = field(default_factory=list)
    invariants: list[CandidateInvariant] = field(default_factory=list)
    edges: list[AttackEdge] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write_json(self, path: str | Path) -> Path:
        import json
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return target
