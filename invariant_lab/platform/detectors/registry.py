from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..types import FindingRecord, ScanResult

DetectorFn = Callable[[ScanResult], list[FindingRecord]]

@dataclass(frozen=True)
class Detector:
    name: str
    description: str
    run: DetectorFn

class DetectorRegistry:
    def __init__(self) -> None:
        self._items: dict[str, Detector] = {}

    def register(self, detector: Detector) -> None:
        if detector.name in self._items:
            raise ValueError(f"detector already registered: {detector.name}")
        self._items[detector.name] = detector

    def all(self) -> tuple[Detector, ...]:
        return tuple(self._items[name] for name in sorted(self._items))

    def run_all(self, result: ScanResult) -> list[FindingRecord]:
        findings: list[FindingRecord] = []
        for detector in self.all():
            findings.extend(detector.run(result))
        return findings
def builtin_registry() -> DetectorRegistry:
    registry = DetectorRegistry()

    def reentrancy(result: ScanResult) -> list[FindingRecord]:
        out = []
        for contract in result.contracts:
            for fn in contract.functions:
                if any(x in fn.body for x in (".call{", ".call(")) and any(
                    token in fn.body.lower() for token in ("transfer", "withdraw", "send")
                ):
                    from ..scanner import _finding
                    out.append(_finding(
                        file=contract.file, line=fn.line, kind="control-flow",
                        title=f"External call in value-changing function {fn.name}",
                        severity="medium", confidence="low",
                        evidence=fn.signature,
                        recommendation="Check checks-effects-interactions ordering and reentrancy guards.",
                        tags=("reentrancy", "external-call"),
                    ))
        return out

    registry.register(Detector(
        "reentrancy-surface",
        "Finds value-changing functions containing low-level external calls.",
        reentrancy,
    ))
    return registry
