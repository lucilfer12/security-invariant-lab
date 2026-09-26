from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

class ProcessState(str, Enum):
    READY="ready"; RUNNING="running"; SLEEPING="sleeping"; EXITED="exited"

@dataclass
class Process:
    pid: int
    name: str
    state: ProcessState = ProcessState.READY
    exit_code: int | None = None
    registers: dict[str, int] = field(default_factory=dict)

class ProcessTable:
    def __init__(self):
        self.next_pid = 1
        self.processes: dict[int, Process] = {}

    def spawn(self, name: str) -> Process:
        process = Process(self.next_pid, name); self.next_pid += 1; self.processes[process.pid] = process
        return process

    def exit(self, pid: int, code: int = 0) -> None:
        process = self.processes[pid]; process.state = ProcessState.EXITED; process.exit_code = code

    def runnable(self) -> list[Process]:
        return [p for p in self.processes.values() if p.state == ProcessState.READY]
