from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

class StateError(ValueError):
    pass

@dataclass
class Account:
    balance: int = 0
    nonce: int = 0

@dataclass(frozen=True)
class Transfer:
    sender: str
    recipient: str
    amount: int
    nonce: int

class StateMachine:
    def __init__(self):
        self.accounts: dict[str, Account] = {}

    def account(self, address: str) -> Account:
        return self.accounts.setdefault(address, Account())

    def validate(self, tx: Transfer) -> None:
        if not tx.sender or not tx.recipient:
            raise StateError("addresses are required")
        if tx.amount <= 0:
            raise StateError("amount must be positive")
        sender = self.account(tx.sender)
        if tx.nonce != sender.nonce:
            raise StateError("invalid nonce")
        if sender.balance < tx.amount:
            raise StateError("insufficient balance")

    def apply(self, tx: Transfer) -> None:
        self.validate(tx)
        sender = self.account(tx.sender)
        recipient = self.account(tx.recipient)
        sender.balance -= tx.amount
        sender.nonce += 1
        recipient.balance += tx.amount

    def fund(self, address: str, amount: int) -> None:
        if amount < 0:
            raise StateError("amount cannot be negative")
        self.account(address).balance += amount

    def state_root(self) -> str:
        leaves = []
        for address, account in sorted(self.accounts.items()):
            raw = json.dumps(
                {"address": address, "balance": account.balance, "nonce": account.nonce},
                sort_keys=True, separators=(",", ":"),
            ).encode()
            leaves.append(hashlib.sha256(raw).hexdigest())
        if not leaves:
            return hashlib.sha256(b"").hexdigest()
        while len(leaves) > 1:
            if len(leaves) % 2:
                leaves.append(leaves[-1])
            leaves = [
                hashlib.sha256((leaves[i] + leaves[i + 1]).encode()).hexdigest()
                for i in range(0, len(leaves), 2)
            ]
        return leaves[0]
