from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DependencyFile:
    path: str
    ecosystem: str
    dependencies: tuple[str, ...]

def inventory_dependencies(root: str | Path) -> list[DependencyFile]:
    root = Path(root)
    output: list[DependencyFile] = []

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        deps = tuple(sorted(set(re.findall(r'"([A-Za-z0-9_.-]+)(?:[<>=!~].*)?"', text))))
        output.append(DependencyFile(str(pyproject), "python", deps))

    req = root / "requirements.txt"
    if req.exists():
        deps = tuple(sorted(
            line.split("==", 1)[0].strip()
            for line in req.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.startswith("#")
        ))
        output.append(DependencyFile(str(req), "python", deps))
    package = root / "package.json"
    if package.exists():
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        deps = tuple(sorted(set(data.get("dependencies", {})) | set(data.get("devDependencies", {}))))
        output.append(DependencyFile(str(package), "node", deps))

    cargo = root / "Cargo.toml"
    if cargo.exists():
        deps = tuple(sorted(set(re.findall(r"(?m)^([A-Za-z0-9_-]+)\s*=", cargo.read_text(encoding="utf-8", errors="replace")))))
        output.append(DependencyFile(str(cargo), "rust", deps))

    gomod = root / "go.mod"
    if gomod.exists():
        deps = tuple(sorted(set(re.findall(r"(?m)^\s*([A-Za-z0-9_.\-/]+)\s+v[0-9][^\s]*$", gomod.read_text(encoding="utf-8", errors="replace")))))
        output.append(DependencyFile(str(gomod), "go", deps))

    return output

def dependency_report(root: str | Path) -> list[dict]:
    return [item.__dict__ for item in inventory_dependencies(root)]
