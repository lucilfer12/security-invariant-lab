from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SourceFinding:
    id: str
    language: str
    kind: str
    file: str
    line: int
    evidence: str
    title: str
    recommendation: str

EXTENSIONS = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".rs": "rust",
    ".go": "go", ".c": "c", ".h": "c", ".cc": "cpp",
    ".cpp": "cpp", ".hpp": "cpp",
}

PATTERNS = {
    "python": [
        (r"\bpickle\.loads\s*\(", "deserialization", "pickle deserialization surface",
         "Prefer authenticated, constrained data formats for untrusted input."),
        (r"\bsubprocess\.[A-Za-z_]+\([^\n]*shell\s*=\s*True", "command-exec",
         "shell=True process execution surface", "Avoid shell interpolation and validate command boundaries."),
        (r"\beval\s*\(", "dynamic-code", "eval() execution surface", "Avoid evaluating untrusted strings as code."),
    ],
    "javascript": [
        (r"\beval\s*\(", "dynamic-code", "eval() execution surface",
         "Avoid dynamic evaluation of untrusted content."),
        (r"innerHTML\s*=", "dom-sink", "innerHTML assignment surface",
         "Use safe DOM APIs or explicit output encoding."),
        (r"child_process\.exec\s*\(", "command-exec", "child_process.exec() surface",
         "Use argument-separated process APIs and strict input validation."),
    ],
    "typescript": [
        (r"\beval\s*\(", "dynamic-code", "eval() execution surface",
         "Avoid dynamic evaluation of untrusted content."),
        (r"innerHTML\s*=", "dom-sink", "innerHTML assignment surface",
         "Use safe DOM APIs or explicit output encoding."),
        (r"child_process\.exec\s*\(", "command-exec", "child_process.exec() surface",
         "Use argument-separated process APIs and strict input validation."),
    ],
    "rust": [
        (r"\bunsafe\s*\{", "unsafe", "unsafe Rust block", "Keep unsafe blocks minimal and document invariants."),
    ],
    "go": [
        (r"\bos/exec\b|\bexec\.Command\s*\(", "command-exec",
         "OS command execution surface", "Use fixed argument boundaries and explicit validation."),
        (r"\bunsafe\.Pointer\b", "unsafe", "unsafe pointer surface",
         "Isolate unsafe conversions and validate memory/lifetime invariants."),
    ],
    "c": [
        (r"\b(strcpy|strcat|sprintf|gets|system)\s*\(", "memory-or-command",
         "legacy memory or command API surface", "Prefer bounded APIs and explicit validation."),
    ],
    "cpp": [
        (r"\b(strcpy|strcat|sprintf|gets|system)\s*\(", "memory-or-command",
         "legacy memory or command API surface", "Prefer bounded APIs and explicit validation."),
    ],
}

def _finding(path: Path, language: str, line: int, kind: str, title: str, evidence: str, recommendation: str):
    digest = hashlib.sha1(f"{path}:{line}:{kind}:{evidence}".encode()).hexdigest()[:10].upper()
    return SourceFinding(
        "SRC-" + digest, language, kind, str(path), line, evidence, title, recommendation
    )
def scan_source_tree(root: str | Path) -> tuple[list[SourceFinding], dict[str, int]]:
    root = Path(root).resolve()
    findings: list[SourceFinding] = []
    counts: dict[str, int] = {}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if any(part in {".git", "node_modules", "venv", ".venv", "out", "cache"} for part in path.parts):
            continue
        language = EXTENSIONS[path.suffix.lower()]
        counts[language] = counts.get(language, 0) + 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for pattern, kind, title, recommendation in PATTERNS.get(language, ()):
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    findings.append(_finding(path, language, line_no, kind, title, match.group(0), recommendation))
    return findings, dict(sorted(counts.items()))

__all__ = ["SourceFinding", "scan_source_tree"]
