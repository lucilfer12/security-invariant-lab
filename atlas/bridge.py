from __future__ import annotations

from pathlib import Path

from invariant_lab.platform.pipeline import forge_test, scan_project

class SecurityBridge:
    """Non-invasive bridge: ATLAS consumes SIL results without replacing SIL."""

    def scan(self, root: str | Path, out: str | Path = ".silab"):
        return scan_project(root, out)

    def test(self, target: str | Path):
        return forge_test(target)
