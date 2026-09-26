from __future__ import annotations

from dataclasses import asdict, dataclass

from .types import ScanResult

@dataclass(frozen=True)
class TaintPath:
    contract: str
    function: str
    source: str
    sink: str
    evidence: str

SOURCES = ("msg.sender", "msg.value", "msg.data", "calldata", "tx.origin")
SINKS = (".call(", ".call{", ".delegatecall(", ".staticcall(", "sstore(")

def taint_paths(result: ScanResult) -> list[TaintPath]:
    paths: list[TaintPath] = []
    for c in result.contracts:
        for f in c.functions:
            body = f.body
            sources = [s for s in SOURCES if s in body]
            sinks = [s for s in SINKS if s in body]
            for source in sources:
                for sink in sinks:
                    paths.append(TaintPath(
                        c.name, f.name, source, sink,
                        f"{source} reaches {sink} in {f.signature}",
                    ))
    return paths

def taint_report(result: ScanResult) -> list[dict]:
    return [asdict(p) for p in taint_paths(result)]
