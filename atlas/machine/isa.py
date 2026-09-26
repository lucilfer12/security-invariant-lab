from __future__ import annotations

from dataclasses import dataclass
import re

MASK = (1 << 64) - 1
OPS = {"NOP": 0, "CONST": 1, "MOV": 2, "ADD": 3, "SUB": 4, "MUL": 5, "DIV": 6,
       "LOAD": 7, "STORE": 8, "JMP": 9, "JZ": 10, "XOR": 11, "HALT": 255}
REV = {v: k for k, v in OPS.items()}

@dataclass(frozen=True)
class Instruction:
    op: str
    a: int = 0
    b: int = 0
    c: int = 0

class Assembler:
    def assemble(self, source: str) -> list[Instruction]:
        labels, rows = {}, []
        for raw in source.splitlines():
            s = raw.split(";", 1)[0].strip()
            if not s:
                continue
            while ":" in s:
                label, s = s.split(":", 1)
                labels[label.strip().lower()] = len(rows)
                s = s.strip()
                if not s:
                    break
            if s:
                rows.append(s)
        out = []
        for s in rows:
            p = [x.strip() for x in re.split(r"[ ,]+", s) if x.strip()]
            op, args = p[0].upper(), []
            for x in p[1:]:
                x = x.lower()
                args.append(int(x[1:]) if x.startswith("r") else (labels[x] if x in labels else int(x, 0)))
            args += [0, 0, 0]
            out.append(Instruction(op, *args[:3]))
        return out

def disassemble(code: list[Instruction]) -> str:
    return "\n".join(f"{i:04d}: {x.op} {x.a} {x.b} {x.c}".rstrip() for i, x in enumerate(code))

class CPU:
    def __init__(self, memory_size: int = 256):
        self.r, self.mem, self.pc, self.halted = [0] * 16, [0] * memory_size, 0, False

    def run(self, code: list[Instruction], max_steps: int = 10000) -> list[dict]:
        trace, steps = [], 0
        while not self.halted and 0 <= self.pc < len(code) and steps < max_steps:
            ins = code[self.pc]
            trace.append({"pc": self.pc, "op": ins.op, "r0": self.r[0]})
            self.pc += 1
            steps += 1
            op, a, b, c = ins.op, ins.a, ins.b, ins.c
            if op == "NOP": pass
            elif op == "CONST": self.r[a] = b & MASK
            elif op == "MOV": self.r[a] = self.r[b]
            elif op == "ADD": self.r[a] = (self.r[b] + self.r[c]) & MASK
            elif op == "SUB": self.r[a] = (self.r[b] - self.r[c]) & MASK
            elif op == "MUL": self.r[a] = (self.r[b] * self.r[c]) & MASK
            elif op == "DIV": self.r[a] = 0 if self.r[c] == 0 else self.r[b] // self.r[c]
            elif op == "LOAD": self.r[a] = self.mem[self.r[b]]
            elif op == "STORE": self.mem[self.r[a]] = self.r[b]
            elif op == "JMP": self.pc = a
            elif op == "JZ": self.pc = b if self.r[a] == 0 else self.pc
            elif op == "XOR": self.r[a] = (self.r[b] ^ self.r[c]) & MASK
            elif op == "HALT": self.halted = True
            else: raise ValueError(f"unknown opcode: {op}")
        if steps >= max_steps:
            raise RuntimeError("instruction budget exceeded")
        return trace

