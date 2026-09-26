from __future__ import annotations

from dataclasses import dataclass
import re

@dataclass(frozen=True)
class SecurityDecision:
    allowed: bool
    reasons: tuple[str, ...]

class PromptGuard:
    """Deterministic pre-tool gate for common prompt-injection and secret-exfiltration patterns."""
    PATTERNS = (
        ("instruction_override", re.compile(r"ignore\s+(all|any|previous|prior)\s+instructions", re.I)),
        ("system_prompt_exfiltration", re.compile(r"(system prompt|hidden instructions|developer message)", re.I)),
        ("credential_exfiltration", re.compile(r"(api[_ -]?key|secret|password|private key).{0,40}(send|print|reveal|export)", re.I)),
        ("unsafe_tool_chaining", re.compile(r"(disable|bypass).{0,30}(sandbox|policy|security)", re.I)),
    )

    def inspect(self, text: str) -> SecurityDecision:
        reasons = tuple(name for name, pattern in self.PATTERNS if pattern.search(text))
        return SecurityDecision(not reasons, reasons)

@dataclass
class ToolGateway:
    guard: PromptGuard
    allowed_tools: frozenset[str]

    def authorize(self, tool: str, context: str) -> SecurityDecision:
        decision = self.guard.inspect(context)
        if not decision.allowed:
            return decision
        if tool not in self.allowed_tools:
            return SecurityDecision(False, ("tool_not_allowlisted",))
        return SecurityDecision(True, ())
