from __future__ import annotations

from dataclasses import dataclass

class Op:
    PUSH=1; ADD=2; MUL=3; STORE=4; LOAD=5; HALT=255

@dataclass
class VM:
    gas: int = 10_000

    def __post_init__(self):
        self.stack: list[int] = []
        self.storage: dict[int, int] = {}
        self.pc = 0
        self.halted = False

    def run(self, code: list[tuple[int, int | None]]) -> int:
        while not self.halted and self.pc < len(code):
            if self.gas <= 0: raise RuntimeError("out of gas")
            op, arg = code[self.pc]; self.pc += 1; self.gas -= 1
            if op == Op.PUSH: self.stack.append(int(arg or 0))
            elif op == Op.ADD: self.stack.append(self.stack.pop()+self.stack.pop())
            elif op == Op.MUL: self.stack.append(self.stack.pop()*self.stack.pop())
            elif op == Op.STORE: self.storage[int(arg or 0)] = self.stack.pop()
            elif op == Op.LOAD: self.stack.append(self.storage.get(int(arg or 0),0))
            elif op == Op.HALT: self.halted = True
            else: raise ValueError(op)
        return self.stack[-1] if self.stack else 0
