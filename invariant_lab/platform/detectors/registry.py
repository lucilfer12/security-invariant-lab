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

def _mk(file, line, kind, title, evidence, recommendation, tags, severity="medium", confidence="low"):
    from ..scanner import _finding
    return _finding(file=file, line=line, kind=kind, title=title, severity=severity,
                    confidence=confidence, evidence=evidence,
                    recommendation=recommendation, tags=tags)

def _functions(result: ScanResult):
    for contract in result.contracts:
        for fn in contract.functions:
            yield contract, fn
def builtin_registry() -> DetectorRegistry:
    registry = DetectorRegistry()

    def reentrancy(result):
        out = []
        for contract, fn in _functions(result):
            body = fn.body.lower()
            if ".call{" in body or ".call(" in body:
                if any(k in body for k in ("withdraw", "release", "transfer", "send")):
                    out.append(_mk(contract.file, fn.line, "reentrancy",
                        f"External call in value-changing function {fn.name}", fn.signature,
                        "Verify checks-effects-interactions and an appropriate reentrancy invariant.",
                        ("reentrancy", "external-call"), "medium"))
        return out

    def replay(result):
        out = []
        for contract, fn in _functions(result):
            body = fn.body.lower()
            if "processed" in body and (".call" in body or "delegatecall" in body):
                if any(k in fn.name.lower() for k in ("execute", "process", "relay", "claim", "release")):
                    out.append(_mk(contract.file, fn.line, "replay",
                        f"Replay-sensitive transition in {fn.name}", fn.signature,
                        "Prove one-time state is committed before any re-entrant or external interaction.",
                        ("replay", "state-machine"), "high", "medium"))
        return out

    def authorization(result):
        out = []
        for contract, fn in _functions(result):
            body = fn.body.lower()
            if "tx.origin" in body:
                out.append(_mk(contract.file, fn.line, "authorization",
                    f"tx.origin used in {fn.name}", "tx.origin",
                    "Use explicit caller/role authorization rather than transaction origin.",
                    ("authorization", "identity"), "medium", "high"))
            if fn.visibility in {"external", "public"} and any(k in fn.name.lower() for k in ("upgrade", "setadmin", "setowner", "pause")):
                if not fn.modifiers and "msg.sender" not in body:
                    out.append(_mk(contract.file, fn.line, "authorization",
                        f"Sensitive entrypoint lacks an obvious authorization check: {fn.name}",
                        fn.signature,
                        "Verify the role/authorization invariant for this privileged operation.",
                        ("authorization", "privileged"), "medium"))
        return out

    def upgrade(result):
        out = []
        for contract, fn in _functions(result):
            body = fn.body.lower()
            if "delegatecall" in body:
                out.append(_mk(contract.file, fn.line, "upgradeability",
                    f"delegatecall boundary in {fn.name}", "delegatecall",
                    "Prove target authorization and storage-layout compatibility.",
                    ("delegatecall", "upgradeability"), "high", "medium"))
        return out
    def arithmetic(result):
        out = []
        for contract, fn in _functions(result):
            body = fn.body.lower()
            if "unchecked" in body:
                out.append(_mk(contract.file, fn.line, "arithmetic",
                    f"Unchecked arithmetic in {fn.name}", "unchecked",
                    "Add explicit bounds or an executable arithmetic invariant.",
                    ("arithmetic", "unchecked"), "medium"))
        return out

    def lifecycle(result):
        out = []
        for contract, fn in _functions(result):
            body = fn.body.lower()
            if "selfdestruct" in body:
                out.append(_mk(contract.file, fn.line, "lifecycle",
                    f"Destructive lifecycle operation in {fn.name}", "selfdestruct",
                    "Verify destruction cannot violate lifecycle or asset-conservation properties.",
                    ("lifecycle", "destructive"), "high"))
            if fn.name.lower() in {"initialize", "init"} and fn.visibility in {"external", "public"}:
                if not any(x in fn.modifiers for x in ("initializer", "reinitializer", "onlyInitializing")):
                    out.append(_mk(contract.file, fn.line, "lifecycle",
                        f"Initializer without an obvious guard: {fn.name}", fn.signature,
                        "Verify initialization can execute exactly in the intended lifecycle state.",
                        ("initializer", "upgradeability"), "medium"))
        return out

    def oracle(result):
        out = []
        for contract, fn in _functions(result):
            body = fn.body.lower()
            if any(k in body for k in ("oracle", "latestrounddata", "getprice")):
                out.append(_mk(contract.file, fn.line, "oracle",
                    f"Oracle-sensitive logic in {fn.name}", fn.signature,
                    "Model freshness, decimals, zero values, source integrity, and manipulation assumptions.",
                    ("oracle", "economic"), "low"))
        return out
    def crypto(result):
        out = []
        for contract, fn in _functions(result):
            body = fn.body.lower()
            if "ecrecover(" in body:
                out.append(_mk(contract.file, fn.line, "cryptography",
                    f"Signature recovery in {fn.name}", "ecrecover",
                    "Verify domain separation, signer validity, nonce usage, and replay resistance.",
                    ("crypto", "signature"), "medium"))
            if "encodepacked" in body:
                out.append(_mk(contract.file, fn.line, "cryptography",
                    f"Packed encoding in {fn.name}", "abi.encodePacked",
                    "Check ambiguity when multiple dynamic values are hashed together.",
                    ("crypto", "encoding"), "low"))
        return out

    def assembly(result):
        out = []
        for contract, fn in _functions(result):
            if "assembly" in fn.body.lower():
                out.append(_mk(contract.file, fn.line, "unsafe",
                    f"Inline assembly in {fn.name}", "assembly",
                    "Review memory, calldata, storage, and arithmetic assumptions explicitly.",
                    ("assembly", "unsafe"), "medium"))
        return out

    registry.register(Detector("assembly-surface", "Inline assembly boundaries.", assembly))
    registry.register(Detector("authorization-surface", "Authorization and privileged entrypoints.", authorization))
    registry.register(Detector("cryptography-surface", "Signature and packed-encoding surfaces.", crypto))
    registry.register(Detector("lifecycle-surface", "Initialization and destructive lifecycle operations.", lifecycle))
    registry.register(Detector("oracle-surface", "Oracle-sensitive logic.", oracle))
    registry.register(Detector("reentrancy-surface", "External calls in value-changing functions.", reentrancy))
    registry.register(Detector("replay-surface", "Replay-sensitive transitions.", replay))
    registry.register(Detector("arithmetic-surface", "Unchecked arithmetic boundaries.", arithmetic))
    registry.register(Detector("upgradeability-surface", "Delegatecall trust boundaries.", upgrade))
    return registry

__all__ = ["Detector", "DetectorRegistry", "builtin_registry"]
