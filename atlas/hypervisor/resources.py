from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VCPU:
    id: int
    guest_id: str
    priority: int = 0


@dataclass
class VCPUScheduler:
    """Deterministic priority scheduler with round-robin fairness."""
    queue: list[VCPU] = field(default_factory=list)
    cursor: int = 0

    def add(self, vcpu: VCPU) -> None:
        if any(x.id == vcpu.id and x.guest_id == vcpu.guest_id for x in self.queue):
            raise ValueError("vCPU already queued")
        self.queue.append(vcpu)
        self.queue.sort(key=lambda x: (-x.priority, x.guest_id, x.id))

    def next(self) -> VCPU | None:
        if not self.queue:
            return None
        self.cursor %= len(self.queue)
        item = self.queue[self.cursor]
        self.cursor = (self.cursor + 1) % len(self.queue)
        return item

    def remove_guest(self, guest_id: str) -> int:
        before = len(self.queue)
        self.queue = [x for x in self.queue if x.guest_id != guest_id]
        self.cursor = min(self.cursor, len(self.queue)) if self.queue else 0
        return before - len(self.queue)


@dataclass
class PageTable:
    page_size: int = 4096
    mappings: dict[int, int] = field(default_factory=dict)

    def map(self, virtual_page: int, physical_page: int) -> None:
        if virtual_page < 0 or physical_page < 0:
            raise ValueError("page numbers must be non-negative")
        self.mappings[virtual_page] = physical_page

    def unmap(self, virtual_page: int) -> int | None:
        return self.mappings.pop(virtual_page, None)

    def translate(self, virtual_address: int) -> int:
        if virtual_address < 0:
            raise ValueError("address must be non-negative")
        page, offset = divmod(virtual_address, self.page_size)
        physical = self.mappings.get(page)
        if physical is None:
            raise MemoryError(f"page fault: virtual page {page}")
        return physical * self.page_size + offset
