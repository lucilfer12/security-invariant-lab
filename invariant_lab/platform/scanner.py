from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from .types import (
    AttackEdge,
    ContractRecord,
    FindingRecord,
    FunctionRecord,
    ScanResult,
)

SKIP_DIRS = {".git", "node_modules", "lib", "out", "cache", "broadcast"}

def _balanced(text: str, start: int) -> str:
    depth = 0
    opened = False
    for i in range(start, len(text)):
        c = text[i]
        if c == "{":
            depth += 1
            opened = True
        elif c == "}":
            depth -= 1
            if opened and depth == 0:
                return text[start + 1:i]
    return text[start + 1:]

def _line(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1

def _contract_blocks(text: str) -> Iterable[tuple[str, str, int]]:
    rx = re.compile(r"\bcontract\s+([A-Za-z_]\w*)(?:\s+is\s+([^\{]+))?\s*\{")
    for m in rx.finditer(text):
        yield m.group(1), m.group(2) or "", m.start(), _balanced(text, m.end() - 1)
def _functions(body: str) -> list[FunctionRecord]:
    rx = re.compile(
        r"\bfunction\s+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*([^\{;]*)\{",
        re.MULTILINE,
    )
    result: list[FunctionRecord] = []
    for m in rx.finditer(body):
        tail = m.group(3)
        fn_body = _balanced(body, m.end() - 1)
        visibility = next(
            (x for x in ("external", "public", "internal", "private")
             if re.search(rf"\b{x}\b", tail)),
            "internal",
        )
        modifiers = tuple(
            x for x in re.findall(r"\b([A-Za-z_]\w*)\b", tail)
            if x not in {"external", "public", "internal", "private", "view", "pure", "payable", "returns", "virtual", "override", "memory", "calldata", "storage"}
        )
        signature = f"{m.group(1)}({m.group(2)})"
        mutating = not re.search(r"\b(view|pure)\b", tail)
        result.append(
            FunctionRecord(
                name=m.group(1),
                visibility=visibility,
                modifiers=modifiers,
                payable=bool(re.search(r"\bpayable\b", tail)),
                mutating=mutating,
                line=_line(body, m.start()),
                signature=signature,
                body=fn_body,
            )
        )
    return result

def _state_variables(body: str) -> list[str]:
    names: list[str] = []
    pattern = re.compile(
        r"(?m)^\s*(?:mapping\s*\([^;]+\)|(?:uint|int|bytes|address|bool|string)(?:\d+)?)\s+([A-Za-z_]\w*)\s*(?:=[^;]+)?;"
    )
    for m in pattern.finditer(body):
        names.append(m.group(1))
    return sorted(set(names))
def _imports(source: str) -> list[str]:
    return re.findall(r'\bimport\s+(?:[^;]*?\s+from\s+)?["\']([^"\']+)["\']\s*;', source)

def _events(body: str) -> list[str]:
    return re.findall(r"\bevent\s+([A-Za-z_]\w*)\s*\([^;]*?\)\s*;", body)

def _calls(body: str) -> tuple[str, ...]:
    calls = []
    for name in re.findall(r"\b([A-Za-z_]\w*)\s*\(", body):
        if name not in {"if", "for", "while", "require", "assert", "revert", "emit", "return", "keccak256", "abi"}:
            calls.append(name)
    return tuple(sorted(set(calls)))

def _finding(
    *,
    file: str,
    line: int,
    kind: str,
    title: str,
    severity: str,
    confidence: str,
    evidence: str,
    recommendation: str,
    tags: tuple[str, ...],
) -> FindingRecord:
    key = f"{kind}:{file}:{line}:{title}"
    import hashlib
    fid = "SIL-" + hashlib.sha1(key.encode()).hexdigest()[:10].upper()
    return FindingRecord(fid, kind, title, severity, confidence, file, line, evidence, recommendation, tags)

PATTERNS = [
    (r"\btx\.origin\b", "authorization", "tx.origin used in security-sensitive code", "medium", "Do not use tx.origin for authorization; use explicit caller roles.", ("auth", "identity")),
    (r"\bdelegatecall\s*\(", "execution", "delegatecall is present", "high", "Review target trust, storage compatibility, and authorization around delegatecall.", ("delegatecall", "upgradeability")),
    (r"\.call\s*\{[^}]*value", "value-flow", "low-level value transfer is present", "medium", "Check return handling, reentrancy ordering, and recipient trust boundaries.", ("call", "value")),
    (r"\bselfdestruct\s*\(", "lifecycle", "selfdestruct is present", "high", "Verify lifecycle assumptions and ensure destruction cannot be reached by unintended callers.", ("lifecycle",)),
    (r"\bassembly\s*\{", "unsafe", "inline assembly is present", "medium", "Audit memory, storage, calldata and arithmetic invariants at the assembly boundary.", ("assembly",)),
    (r"\bunchecked\s*\{", "arithmetic", "unchecked arithmetic block is present", "medium", "Prove bounds around every unchecked operation.", ("arithmetic",)),
    (r"\bblock\.timestamp\b", "time", "block timestamp influences behavior", "info", "Model timestamp drift and miner/validator influence where security-sensitive.", ("time", "environment")),
    (r"\babi\.encodePacked\s*\(", "crypto", "abi.encodePacked is used", "info", "Check hash-domain ambiguity when multiple dynamic values are combined.", ("hashing", "encoding")),
    (r"\becrecover\s*\(", "crypto", "ecrecover is used", "info", "Verify domain separation, nonce handling, signer zero checks and replay resistance.", ("signature", "replay")),
]
def scan_solidity_file(path: Path) -> tuple[list[ContractRecord], list[FindingRecord], list[AttackEdge]]:
    source = path.read_text(encoding="utf-8", errors="replace")
    contracts: list[ContractRecord] = []
    findings: list[FindingRecord] = []
    edges: list[AttackEdge] = []

    for name, bases, start, body in _contract_blocks(source):
        functions = _functions(body)
        contract = ContractRecord(
            name=name,
            file=str(path),
            line=_line(source, start),
            bases=tuple(x.strip() for x in bases.split(",") if x.strip()),
            functions=tuple(functions),
            state_variables=tuple(_state_variables(body)),
            events=tuple(_events(body)),
            imports=tuple(_imports(source)),
        )
        contracts.append(contract)

        for fn in functions:
            node = f"{name}.{fn.name}"
            for target in _calls(fn.body):
                edges.append(AttackEdge(node, f"{name}.{target}", "call", f"{fn.signature} calls {target}()"))
            if fn.visibility in {"external", "public"}:
                edges.append(AttackEdge("ATTACKER", node, "entrypoint", f"{fn.visibility} function"))
                if fn.mutating:
                    edges.append(AttackEdge(node, "STATE", "mutation", "mutating entrypoint"))
            if fn.modifiers:
                for modifier in fn.modifiers:
                    edges.append(AttackEdge(f"ROLE:{modifier}", node, "authorization", f"modifier {modifier}"))

    for pattern, kind, title, severity, recommendation, tags in PATTERNS:
        for m in re.finditer(pattern, source, re.IGNORECASE):
            confidence = "medium" if severity in {"high", "medium"} else "low"
            findings.append(_finding(
                file=str(path), line=_line(source, m.start()), kind=kind, title=title,
                severity=severity, confidence=confidence, evidence=m.group(0),
                recommendation=recommendation, tags=tags,
            ))

    return contracts, findings, edges
class SolidityScanner:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def files(self) -> list[Path]:
        if self.root.is_file():
            return [self.root] if self.root.suffix.lower() == ".sol" else []
        paths: list[Path] = []
        for path in self.root.rglob("*.sol"):
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            paths.append(path)
        return sorted(paths)

    def scan(self) -> ScanResult:
        result = ScanResult(root=str(self.root))
        for path in self.files():
            try:
                contracts, findings, edges = scan_solidity_file(path)
            except OSError as exc:
                findings = [_finding(
                    file=str(path), line=1, kind="tooling", title="Unable to read Solidity source",
                    severity="info", confidence="high", evidence=str(exc),
                    recommendation="Check filesystem permissions and encoding.", tags=("tooling",),
                )]
                contracts, edges = [], []
            result.contracts.extend(contracts)
            result.findings.extend(findings)
            result.edges.extend(edges)
        result.metrics = {
            "solidity_files": len(self.files()),
            "contracts": len(result.contracts),
            "functions": sum(len(c.functions) for c in result.contracts),
            "state_variables": sum(len(c.state_variables) for c in result.contracts),
            "external_entrypoints": sum(
                sum(1 for f in c.functions if f.visibility in {"external", "public"})
                for c in result.contracts
            ),
            "findings": len(result.findings),
            "graph_edges": len(result.edges),
        }
        return result
def attack_surface(result: ScanResult) -> dict:
    privileged, entrypoints, external_calls, delegates, low_level = [], [], [], [], []
    for contract in result.contracts:
        for fn in contract.functions:
            name = f"{contract.name}.{fn.signature}"
            if fn.modifiers:
                privileged.append(name)
            if fn.visibility in {"external", "public"}:
                entrypoints.append(name)
            if any(x in fn.body for x in (".call(", ".call{", ".staticcall(")):
                low_level.append(name)
            if "delegatecall(" in fn.body:
                delegates.append(name)
            if any(x in fn.body for x in (".call(", ".staticcall(", ".delegatecall(")):
                external_calls.append(name)
    return {
        "contracts": [c.name for c in result.contracts],
        "external_entrypoints": sorted(set(entrypoints)),
        "privileged_functions": sorted(set(privileged)),
        "external_call_sites": sorted(set(external_calls)),
        "delegatecall_sites": sorted(set(delegates)),
        "low_level_call_sites": sorted(set(low_level)),
        "state_variables": sorted({v for c in result.contracts for v in c.state_variables}),
    }
__all__ = ["SolidityScanner", "scan_solidity_file", "attack_surface"]
