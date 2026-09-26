from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class Rule:
    effect: str
    role: str
    action: str
    resource: str

    def matches(self, role: str, action: str, resource: str) -> bool:
        return self.role in (role, "*") and self.action in (action, "*") and self.resource in (resource, "*")

@dataclass(frozen=True)
class Policy:
    rules: tuple[Rule, ...]

    def decide(self, role: str, action: str, resource: str) -> bool:
        decision = False
        for rule in self.rules:
            if rule.matches(role, action, resource):
                decision = rule.effect == "allow"
        return decision

def parse_policy(text: str) -> Policy:
    rules = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        parts = {k: v for k, v in (x.split("=", 1) for x in s.split() if "=" in x)}
        effect = s.split()[0].lower()
        if effect not in {"allow", "deny"}:
            raise ValueError(f"invalid effect: {effect}")
        rules.append(Rule(effect, parts.get("role", "*"), parts.get("action", "*"), parts.get("resource", "*")))
    return Policy(tuple(rules))
