from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ToolPolicy:
    allowed: frozenset[str] = frozenset()
    max_calls: int = 16

@dataclass
class AgentSandbox:
    policy: ToolPolicy
    calls: int = 0
    secrets: tuple[str, ...] = ()

    def authorize(self, tool: str) -> bool:
        return self.calls < self.policy.max_calls and tool in self.policy.allowed

    def invoke(self, tool: str) -> None:
        if not self.authorize(tool):
            raise PermissionError(f"tool denied: {tool}")
        self.calls += 1

    def redact(self, text: str) -> str:
        for secret in self.secrets:
            if secret:
                text = text.replace(secret, "[REDACTED]")
        return text
