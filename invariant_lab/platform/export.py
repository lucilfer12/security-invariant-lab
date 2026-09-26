from __future__ import annotations

import json
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from .types import ScanResult

def to_sarif(result: ScanResult) -> dict:
    rules = {}
    results = []
    for finding in result.findings:
        rules.setdefault(finding.kind, {
            "id": finding.kind,
            "name": finding.kind,
            "shortDescription": {"text": finding.title},
        })
        results.append({
            "ruleId": finding.kind,
            "level": "warning" if finding.severity in {"medium", "high"} else "note",
            "message": {"text": finding.title + ": " + finding.evidence},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": finding.file},
                "region": {"startLine": finding.line},
            }}],
        })
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [{
            "tool": {"driver": {
                "name": "Security Invariant Lab",
                "semanticVersion": "0.5.0",
                "rules": list(rules.values()),
            }},
            "results": results,
        }],
    }

def to_junit(result: ScanResult) -> bytes:
    suite = Element("testsuite", name="security-invariant-lab")
    suite.set("tests", str(max(1, len(result.findings))))
    suite.set("failures", str(len(result.findings)))
    for finding in result.findings:
        case = SubElement(suite, "testcase", classname=finding.kind, name=finding.id)
        failure = SubElement(case, "failure", message=finding.title)
        failure.text = f"{finding.file}:{finding.line}\n{finding.evidence}"
    return tostring(suite, encoding="utf-8", xml_declaration=True)
def write_exports(result: ScanResult, out_dir: str | Path) -> dict[str, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    sarif = out / "report.sarif.json"
    junit = out / "report.junit.xml"
    dataset = out / "research-dataset.json"
    sarif.write_text(json.dumps(to_sarif(result), indent=2) + "\n", encoding="utf-8")
    junit.write_bytes(to_junit(result))
    dataset.write_text(json.dumps({
        "schema_version": "1.0",
        "root": result.root,
        "findings": [f.__dict__ for f in result.findings],
        "properties": [p.__dict__ for p in result.invariants],
    }, indent=2, default=str) + "\n", encoding="utf-8")
    return {"sarif": sarif, "junit": junit, "dataset": dataset}
