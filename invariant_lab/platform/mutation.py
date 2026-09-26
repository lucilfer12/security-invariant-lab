from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Mutation:
    id: str
    file: str
    line: int
    kind: str
    original: str
    replacement: str
    rationale: str

OPS = (
    (r">=", ">", "boundary-tightening"),
    (r"<=", "<", "boundary-tightening"),
    (r"==", "!=", "equality-inversion"),
    (r"&&", "||", "boolean-relaxation"),
    (r"\+\+", "--", "counter-direction"),
    (r"require\s*\(([^;]+)\);", "require(true);", "guard-removal"),
)

def _id(file: str, line: int, kind: str, original: str) -> str:
    raw = f"{file}:{line}:{kind}:{original}"
    return "MUT-" + hashlib.sha1(raw.encode()).hexdigest()[:10].upper()

def suggest_mutations(path: str | Path) -> list[Mutation]:
    source_path = Path(path)
    text = source_path.read_text(encoding="utf-8", errors="replace")
    out: list[Mutation] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for pattern, replacement, kind in OPS:
            match = re.search(pattern, line)
            if not match:
                continue
            original = match.group(0)
            repl = re.sub(pattern, replacement, original, count=1)
            if repl == original:
                continue
            out.append(Mutation(
                _id(str(source_path), line_no, kind, original),
                str(source_path), line_no, kind, original, repl,
                "Generated candidate mutation; it is never written over the original source.",
            ))
    seen = {m.id: m for m in out}
    return list(seen.values())

def apply_mutation_to_text(source: str, mutation: Mutation) -> str:
    lines = source.splitlines(keepends=True)
    index = mutation.line - 1
    if index < 0 or index >= len(lines):
        raise IndexError("mutation line is outside source")
    if mutation.original not in lines[index]:
        raise ValueError("mutation no longer matches source")
    lines[index] = lines[index].replace(mutation.original, mutation.replacement, 1)
    return "".join(lines)

__all__ = ["Mutation", "suggest_mutations", "apply_mutation_to_text"]
