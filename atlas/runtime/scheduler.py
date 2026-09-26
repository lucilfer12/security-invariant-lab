from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Callable, Any

@dataclass
class Task:
    id: str
    fn: Callable[[], Any]
    priority: int = 0
    budget: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class TaskResult:
    task_id: str
    status: str
    value: Any = None
    error: str | None = None
    ticks: int = 0

class Scheduler:
    def __init__(self):
        self.queues: dict[int, deque[Task]] = {}
        self.clock = 0

    def submit(self, task: Task) -> None:
        self.queues.setdefault(task.priority, deque()).append(task)

    def run(self, max_ticks: int = 1000) -> list[TaskResult]:
        out = []
        while self.queues and self.clock < max_ticks:
            p = max(self.queues)
            q = self.queues[p]
            task = q.popleft()
            self.clock += 1
            try:
                out.append(TaskResult(task.id, "done", task.fn(), ticks=1))
            except Exception as exc:
                out.append(TaskResult(task.id, "failed", error=str(exc), ticks=1))
            if not q:
                del self.queues[p]
        return out

