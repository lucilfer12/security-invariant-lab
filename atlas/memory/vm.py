from __future__ import annotations

from dataclasses import dataclass
from enum import Flag, auto

class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXEC = auto()

@dataclass(frozen=True)
class Page:
    frame: int
    permission: Permission

class PageTable:
    def __init__(self, page_size: int = 4096):
        self.page_size = page_size
        self.pages: dict[int, Page] = {}

    def map(self, virtual_page: int, frame: int, permission: Permission) -> None:
        if virtual_page in self.pages:
            raise ValueError("virtual page already mapped")
        self.pages[virtual_page] = Page(frame, permission)

class VirtualMemory:
    def __init__(self, page_size: int = 4096):
        self.table = PageTable(page_size)
        self.frames: dict[int, bytearray] = {}

    def map(self, virtual_page: int, frame: int, permission: Permission) -> None:
        self.table.map(virtual_page, frame, permission)
        self.frames.setdefault(frame, bytearray(self.table.page_size))

    def _translate(self, address: int, needed: Permission) -> tuple[bytearray, int]:
        page, offset = divmod(address, self.table.page_size)
        mapping = self.table.pages.get(page)
        if mapping is None or not (mapping.permission & needed):
            raise PermissionError("page fault: mapping or permission denied")
        return self.frames[mapping.frame], offset

    def read(self, address: int, size: int = 1) -> bytes:
        out = bytearray()
        for i in range(size):
            frame, off = self._translate(address + i, Permission.READ)
            out.append(frame[off])
        return bytes(out)

    def write(self, address: int, data: bytes) -> None:
        for i, byte in enumerate(data):
            frame, off = self._translate(address + i, Permission.WRITE)
            frame[off] = byte
