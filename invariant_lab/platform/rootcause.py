from __future__ import annotations

from .taint import taint_paths
from .types import ScanResult

def root_cause_candidates(result: ScanResult) -> list[dict]:
    paths = taint_paths(result)
    out = []
    for finding in result.findings:
        related = [
            p for p in paths
            if p.contract in finding.file or p.sink in finding.evidence
        ]
        out.append({
            "finding": finding.id,
            "hypotheses": [
                "unvalidated state transition",
                "authorization or trust-boundary mismatch",
                "external interaction before invariant-preserving state update",
                "accounting or lifecycle assumption",
            ],
            "taint_links": [p.evidence for p in related[:12]],
        })
    return out
