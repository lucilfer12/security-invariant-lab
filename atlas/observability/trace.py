from __future__ import annotations

from dataclasses import dataclass, field
import time

@dataclass
class Counter:
    value: int = 0

    def inc(self, amount: int = 1) -> int:
        self.value += amount
        return self.value

@dataclass
class Span:
    name: str
    start_ns: int = field(default_factory=time.time_ns)
    end_ns: int | None = None
    attributes: dict[str, str] = field(default_factory=dict)

    def finish(self) -> None:
        self.end_ns = time.time_ns()

class Tracer:
    def __init__(self):
        self.spans: list[Span] = []

    def span(self, name: str, **attributes: str) -> Span:
        s = Span(name, attributes=dict(attributes))
        self.spans.append(s)
        return s
