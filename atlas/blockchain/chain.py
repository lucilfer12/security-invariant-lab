from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import time

def merkle_root(items: list[str]) -> str:
    if not items:
        return hashlib.sha256(b"").hexdigest()
    level = list(items)
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256((level[i] + level[i + 1]).encode()).hexdigest()
                 for i in range(0, len(level), 2)]
    return level[0]

@dataclass(frozen=True)
class Transaction:
    sender: str
    nonce: int
    payload: dict

    def digest(self) -> str:
        raw = json.dumps(self.__dict__, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()

@dataclass(frozen=True)
class Block:
    height: int
    previous: str
    timestamp: int
    transactions: tuple[Transaction, ...]

    def digest(self) -> str:
        txs = [tx.digest() for tx in self.transactions]
        body = f"{self.height}|{self.previous}|{self.timestamp}|{merkle_root(txs)}"
        return hashlib.sha256(body.encode()).hexdigest()

class Chain:
    def __init__(self):
        self.blocks: list[Block] = []

    def append(self, transactions: list[Transaction]) -> Block:
        previous = self.blocks[-1].digest() if self.blocks else "GENESIS"
        block = Block(len(self.blocks), previous, time.time_ns(), tuple(transactions))
        self.blocks.append(block)
        return block

    def verify(self) -> bool:
        previous = "GENESIS"
        for block in self.blocks:
            if block.previous != previous:
                return False
            previous = block.digest()
        return True
