from __future__ import annotations

from dataclasses import dataclass

from .graphs import GraphSnapshot
from .types import ScanResult

@dataclass(frozen=True)
class EvidenceGraph:
    nodes: tuple[dict, ...]
    edges: tuple[dict, ...]

    def to_dict(self) -> dict:
        return {"nodes": list(self.nodes), "edges": list(self.edges)}

def build_evidence_graph(result: ScanResult, graph: GraphSnapshot) -> EvidenceGraph:
    nodes = []
    edges = []
    for contract in result.contracts:
        node = {"id": contract.name, "type": "contract", "label": contract.name}
        nodes.append(node)
        for fn in contract.functions:
            fid = f"{contract.name}.{fn.name}"
            nodes.append({"id": fid, "type": "function", "label": fn.signature})
            edges.append({"source": contract.name, "target": fid, "kind": "contains"})
    for prop in result.invariants:
        nodes.append({"id": prop.name, "type": "property", "label": prop.expression})
    for finding in result.findings:
        nodes.append({"id": finding.id, "type": "finding", "label": finding.title})
    edges.extend({
        "source": e.source, "target": e.target, "kind": e.kind, "evidence": e.evidence
    } for e in graph.edges)
    return EvidenceGraph(tuple(nodes), tuple(edges))

__all__ = ["EvidenceGraph", "build_evidence_graph"]
