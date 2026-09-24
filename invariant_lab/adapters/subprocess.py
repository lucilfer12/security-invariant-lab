from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def run_command(argv: list[str], *, cwd: str | None = None, timeout: int = 60) -> CommandResult:
    """Run an explicitly supplied local command for authorized test harnesses."""
    completed = subprocess.run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)
