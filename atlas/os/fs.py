from __future__ import annotations

from dataclasses import dataclass, field

@dataclass
class Node:
    name: str
    directory: bool
    data: bytearray = field(default_factory=bytearray)
    children: dict[str, "Node"] = field(default_factory=dict)

class FileSystem:
    def __init__(self):
        self.root = Node("/", True)

    def _node(self, path: str, create: bool = False) -> Node:
        current = self.root
        parts = [p for p in path.split("/") if p]
        for part in parts:
            if create: current.children.setdefault(part, Node(part, False))
            current = current.children[part]
        return current

    def mkdir(self, path: str) -> None:
        node = self._node(path, True); node.directory = True

    def write(self, path: str, data: bytes) -> None:
        node = self._node(path, True); node.data = bytearray(data)

    def read(self, path: str) -> bytes:
        return bytes(self._node(path).data)

    def listdir(self, path: str = "/") -> list[str]:
        return sorted(self._node(path).children)
