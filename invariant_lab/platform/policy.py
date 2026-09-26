from __future__ import annotations

from dataclasses import dataclass

LEVELS = {"none": 0, "info": 1, "low": 2, "medium": 3, "high": 4}

@dataclass(frozen=True)
class SecurityPolicy:
    fail_on: str = "high"
    max_findings: int | None = None

    def should_fail(self, findings) -> bool:
        threshold = LEVELS.get(self.fail_on, LEVELS["high"])
        if self.max_findings is not None and len(findings) > self.max_findings:
            return True
        for finding in findings:
            if LEVELS.get(finding.severity, LEVELS["medium"]) >= threshold:
                return True
        return False

    def to_dict(self) -> dict:
        return {"fail_on": self.fail_on, "max_findings": self.max_findings}

def from_file(path) -> SecurityPolicy:
    import json
    data = json.loads(open(path, encoding="utf-8").read())
    fail_on = str(data.get("fail_on", "high")).lower()
    if fail_on not in LEVELS:
        raise ValueError(f"unknown fail_on: {fail_on}")
    return SecurityPolicy(fail_on, data.get("max_findings"))
