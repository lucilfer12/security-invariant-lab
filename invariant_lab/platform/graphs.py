from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .types import AttackEdge, ScanResult

@dataclass(frozen=True)
class GraphSnapshot:
    nodes: tuple[str, ...]
    edges: tuple[AttackEdge, ...]

    def to_dict(self) -> dict:
        return {
            "nodes": list(self.nodes),
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "kind": e.kind,
                    "evidence": e.evidence,
                }
                for e in self.edges
            ],
        }

def build_graph(result: ScanResult) -> GraphSnapshot:
    nodes: set[str] = {"ATTACKER", "STATE"}
    edges = list(result.edges)
    for contract in result.contracts:
        nodes.add(contract.name)
        for fn in contract.functions:
            nodes.add(f"{contract.name}.{fn.name}")
            for variable in contract.state_variables:
                nodes.add(f"STATE:{contract.name}.{variable}")
                if fn.mutating and variable.lower() in fn.body.lower():
                    edges.append(AttackEdge(
                        f"{contract.name}.{fn.name}",
                        f"STATE:{contract.name}.{variable}",
                        "data-flow",
                        f"{fn.name} references {variable}",
                    ))
    for finding in result.findings:
        nodes.add(finding.id)
        edges.append(AttackEdge(
            finding.file,
            finding.id,
            "evidence",
            f"{finding.kind} at line {finding.line}",
        ))
    return GraphSnapshot(tuple(sorted(nodes)), tuple(edges))

def attack_paths(graph: GraphSnapshot, max_depth: int = 6) -> list[list[str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for edge in graph.edges:
        adjacency[edge.source].append(edge.target)
    paths: list[list[str]] = []

    def walk(node: str, path: list[str]) -> None:
        if len(path) >= 2 and node in {"STATE"}:
            paths.append(path)
        if len(path) >= max_depth:
            return
        for nxt in sorted(adjacency.get(node, [])):
            if nxt in path:
                continue
            walk(nxt, path + [nxt])
    walk("ATTACKER", ["ATTACKER"])
    return paths[:500]

def to_dot(graph: GraphSnapshot) -> str:
    lines = ["digraph SecurityGraph {"]
    for node in graph.nodes:
        safe = node.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'  "{safe}";')
    for edge in graph.edges:
        s = edge.source.replace('"', '\\"')
        t = edge.target.replace('"', '\\"')
        lines.append(f'  "{s}" -> "{t}" [label="{edge.kind}"];')
    lines.append("}")
    return "\n".join(lines) + "\n"

__all__ = ["GraphSnapshot", "build_graph", "attack_paths", "to_dot"]
