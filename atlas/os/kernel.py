from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from .process import Process, ProcessState, ProcessTable

class KernelMode(str, Enum):
    BOOT = "boot"
    RUNNING = "running"
    PANIC = "panic"

@dataclass(frozen=True)
class Syscall:
    number: int
    name: str

class Kernel:
    """Deterministic kernel lifecycle with a syscall table and preemptive tick model."""
    SYSCALLS = (
        Syscall(0, "yield"),
        Syscall(1, "exit"),
        Syscall(2, "write"),
        Syscall(3, "sleep"),
    )

    def __init__(self):
        self.mode = KernelMode.BOOT
        self.processes = ProcessTable()
        self.ticks = 0
        self.current_pid: int | None = None
        self.logs: list[str] = []

    def boot(self) -> None:
        if self.mode is not KernelMode.BOOT:
            raise RuntimeError("kernel already booted")
        self.mode = KernelMode.RUNNING
        init = self.processes.spawn("init")
        self.current_pid = init.pid
        self.logs.append("kernel:boot")

    def schedule(self) -> Process | None:
        runnable = self.processes.runnable()
        if not runnable:
            self.current_pid = None
            return None
        if self.current_pid in [p.pid for p in runnable]:
            idx = next(i for i,p in enumerate(runnable) if p.pid == self.current_pid)
            selected = runnable[(idx + 1) % len(runnable)]
        else:
            selected = runnable[0]
        if self.current_pid is not None and self.current_pid in self.processes.processes:
            old = self.processes.processes[self.current_pid]
            if old.state is ProcessState.RUNNING:
                old.state = ProcessState.READY
        selected.state = ProcessState.RUNNING
        self.current_pid = selected.pid
        return selected

    def tick(self, quantum: int = 1) -> Process | None:
        if self.mode is not KernelMode.RUNNING:
            raise RuntimeError("kernel is not running")
        self.ticks += max(1, quantum)
        return self.schedule()

    def syscall(self, pid: int, number: int, value: int | bytes | None = None) -> int | None:
        if self.mode is not KernelMode.RUNNING:
            raise RuntimeError("kernel is not running")
        if pid not in self.processes.processes:
            raise ValueError("unknown process")
        if number == 0:
            return self.tick()
        if number == 1:
            self.processes.exit(pid, int(value or 0))
            if pid == self.current_pid:
                self.current_pid = None
                self.schedule()
            return None
        if number == 2:
            self.logs.append(bytes(value or b"").decode(errors="replace"))
            return len(value or b"")
        if number == 3:
            self.processes.processes[pid].state = ProcessState.SLEEPING
            return None
        raise ValueError("unknown syscall")
