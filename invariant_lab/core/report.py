from __future__ import annotations

from pathlib import Path

from .engine import CaseResult


def to_markdown(result: CaseResult) -> str:
    lines = [f"# Case: {result.case.name}", "", f"**Status:** {'PASS' if result.passed else 'FAIL'}", ""]
    if result.finding:
        lines += [f"## Invariant\n\n`{result.finding.invariant}`", "", result.finding.message, ""]
        lines += ["## Trace", "", "```text", "\n".join(e.name for e in result.finding.trace), "```", ""]
        if result.finding.before:
            lines += ["## Before", "", "```json", str(result.finding.before.data), "```", ""]
        if result.finding.after:
            lines += ["## After", "", "```json", str(result.finding.after.data), "```", ""]
    return "\n".join(lines)


def write_markdown(result: CaseResult, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(to_markdown(result), encoding="utf-8")
    return target
