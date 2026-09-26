from __future__ import annotations

import hashlib
from dataclasses import dataclass


def _hash(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


@dataclass(frozen=True)
class MerkleProof:
    index: int
    leaf: bytes
    siblings: tuple[bytes, ...]


class MerkleTree:
    def __init__(self, leaves: list[bytes]):
        if not leaves:
            raise ValueError("at least one leaf is required")
        self.leaves = list(leaves)
        self.levels: list[list[bytes]] = [[_hash(leaf) for leaf in self.leaves]]
        while len(self.levels[-1]) > 1:
            current = self.levels[-1]
            parent: list[bytes] = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                parent.append(_hash(left + right))
            self.levels.append(parent)

    @property
    def root(self) -> bytes:
        return self.levels[-1][0]

    def proof(self, index: int) -> MerkleProof:
        if index < 0 or index >= len(self.leaves):
            raise IndexError(index)
        siblings: list[bytes] = []
        position = index
        for level in self.levels[:-1]:
            sibling = position ^ 1
            siblings.append(level[sibling] if sibling < len(level) else level[position])
            position //= 2
        return MerkleProof(index, self.leaves[index], tuple(siblings))

    @staticmethod
    def verify(root: bytes, proof: MerkleProof) -> bool:
        node = _hash(proof.leaf)
        position = proof.index
        for sibling in proof.siblings:
            node = _hash(node + sibling) if position % 2 == 0 else _hash(sibling + node)
            position //= 2
        return node == root
