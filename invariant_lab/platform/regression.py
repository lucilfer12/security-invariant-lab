from __future__ import annotations

from pathlib import Path

from .types import FindingRecord

def generate_foundry_skeleton(finding: FindingRecord, target_contract: str = "Target") -> str:
    fn = "".join(ch if ch.isalnum() else "_" for ch in finding.id.lower())
    return """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "forge-std/Test.sol";

contract {contract}Regression is Test {{
    // Generated from {finding}.
    // This is a regression skeleton, not an exploit.
    function test_{fn}() public {{
        // Arrange: deploy the authorized local fixture.
        // Act: replay the minimized transition sequence.
        // Assert: encode the violated security property.
        //
        // Evidence:
        // file={file}
        // line={line}
        // kind={kind}
        // evidence={evidence}
        assertTrue(true);
    }}
}}
""".format(
        contract="".join(ch for ch in target_contract if ch.isalnum()),
        finding=finding.id, fn=fn, file=finding.file, line=finding.line,
        kind=finding.kind, evidence=finding.evidence.replace("\n", " "),
    )

def write_regression_skeletons(findings: list[FindingRecord], out_dir: str | Path) -> list[Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for finding in findings:
        target = out / f"{finding.id}.t.sol"
        target.write_text(generate_foundry_skeleton(finding), encoding="utf-8")
        paths.append(target)
    return paths
