from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class ForgeResult:
    available: bool
    returncode: int | None
    command: tuple[str, ...]
    stdout: str = ""
    stderr: str = ""

class FoundryAdapter:
    """Authorized local EVM adapter. Never chooses a live target or RPC automatically."""

    def __init__(self, project: str | Path):
        self.project = Path(project).resolve()

    @property
    def forge(self) -> str | None:
        return shutil.which("forge")

    @property
    def anvil(self) -> str | None:
        return shutil.which("anvil")

    def status(self) -> dict[str, Any]:
        return {"forge": bool(self.forge), "anvil": bool(self.anvil), "project": str(self.project)}

    def test(self, verbose: int = 2, timeout: int = 300) -> ForgeResult:
        if not self.forge:
            return ForgeResult(False, None, ("forge", "test"), stderr="forge not found on PATH")
        command = ("forge", "test", "-" + "v" * max(1, min(verbose, 5)))
        try:
            proc = subprocess.run(command, cwd=self.project, text=True,
                                  capture_output=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired as exc:
            return ForgeResult(True, None, command, (exc.stdout or "")[-12000:], "timeout")
        return ForgeResult(True, proc.returncode, command, proc.stdout[-12000:], proc.stderr[-6000:])

    def build(self, timeout: int = 300) -> ForgeResult:
        if not self.forge:
            return ForgeResult(False, None, ("forge", "build"), stderr="forge not found on PATH")
        command = ("forge", "build")
        proc = subprocess.run(command, cwd=self.project, text=True,
                              capture_output=True, timeout=timeout, check=False)
        return ForgeResult(True, proc.returncode, command, proc.stdout[-8000:], proc.stderr[-6000:])

    def env_report(self) -> dict[str, Any]:
        return {
            "foundry": self.status(),
            "foundry_toml": str(self.project / "foundry.toml") if (self.project / "foundry.toml").exists() else None,
        }

    def write_result(self, result: ForgeResult, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({
            "available": result.available, "returncode": result.returncode,
            "command": list(result.command), "stdout": result.stdout, "stderr": result.stderr,
        }, indent=2) + "\n", encoding="utf-8")
        return target
