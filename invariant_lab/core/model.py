from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, "__dict__"):
        return _json_safe(vars(value))
    return value


@dataclass(frozen=True)
class Event:
    name: str
    params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "params": _json_safe(self.params)}


@dataclass(frozen=True)
class StateSnapshot:
    label: str
    data: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "data": _json_safe(self.data)}


@dataclass(frozen=True)
class Finding:
    invariant: str
    message: str
    trace: tuple[Event, ...]
    before: StateSnapshot | None = None
    after: StateSnapshot | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant": self.invariant,
            "message": self.message,
            "trace": [event.to_dict() for event in self.trace],
            "before": self.before.to_dict() if self.before else None,
            "after": self.after.to_dict() if self.after else None,
            "metadata": _json_safe(self.metadata),
        }
