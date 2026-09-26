from __future__ import annotations

from dataclasses import dataclass
from .vm import Permission, VirtualMemory

@dataclass
class Frame:
    id: int
    refcount: int = 1

class CopyOnWriteMemory:
    """Page-granular copy-on-write layer over the existing VirtualMemory model."""
    def __init__(self, page_size: int = 4096):
        self.vm = VirtualMemory(page_size)
        self.frames: dict[int, Frame] = {}
        self.next_frame = 1

    def allocate(self, virtual_page: int, permission: Permission) -> int:
        frame = self.next_frame
        self.next_frame += 1
        self.vm.map(virtual_page, frame, permission)
        self.frames[frame] = Frame(frame)
        return frame

    def fork(self, parent_pages: list[int]) -> "CopyOnWriteMemory":
        child = CopyOnWriteMemory(self.vm.table.page_size)
        for page in parent_pages:
            mapping = self.vm.table.pages.get(page)
            if mapping is None:
                raise ValueError("page is not mapped")
            self.frames[mapping.frame].refcount += 1
            child.vm.map(page, mapping.frame, mapping.permission)
            child.frames[mapping.frame] = self.frames[mapping.frame]
        child.next_frame = self.next_frame
        return child

    def cow_clone_page(self, virtual_page: int) -> int:
        mapping = self.vm.table.pages[virtual_page]
        frame = self.frames[mapping.frame]
        if frame.refcount <= 1:
            return mapping.frame
        old_data = bytes(self.vm.frames[mapping.frame])
        frame.refcount -= 1
        new_frame = self.next_frame
        self.next_frame += 1
        self.vm.frames[new_frame] = bytearray(old_data)
        self.vm.table.pages[virtual_page] = type(mapping)(new_frame, mapping.permission)
        self.frames[new_frame] = Frame(new_frame)
        return new_frame

    def write(self, address: int, data: bytes) -> None:
        page = address // self.vm.table.page_size
        self.cow_clone_page(page)
        self.vm.write(address, data)
