from __future__ import annotations

from dataclasses import dataclass
import heapq

@dataclass(order=True, frozen=True)
class Event:
    tick: int
    target: str
    kind: str
    value: object = None

class Cluster:
    def __init__(self):
        self.now = 0
        self.nodes: dict[str, bool] = {}
        self.queue: list[Event] = []

    def add_node(self, node: str, up: bool = True) -> None:
        self.nodes[node] = up

    def schedule(self, event: Event) -> None:
        heapq.heappush(self.queue, event)

    def run(self, until: int = 1000) -> list[Event]:
        out = []
        while self.queue and self.queue[0].tick <= until:
            event = heapq.heappop(self.queue); self.now = event.tick
            if event.kind == "down": self.nodes[event.target] = False
            elif event.kind == "up": self.nodes[event.target] = True
            out.append(event)
        return out
