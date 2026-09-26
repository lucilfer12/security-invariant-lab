from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(frozen=True)
class IRInstruction:
    op: str
    args: tuple[str, ...] = ()

@dataclass
class IRFunction:
    name: str
    params: tuple[str, ...]
    instructions: list[IRInstruction] = field(default_factory=list)

    def emit(self, op: str, *args: str) -> None:
        self.instructions.append(IRInstruction(op, tuple(args)))

@dataclass
class IRModule:
    functions: dict[str, IRFunction] = field(default_factory=dict)

    def add(self, fn: IRFunction) -> None:
        self.functions[fn.name] = fn

    def optimize(self) -> int:
        folded = 0
        for fn in self.functions.values():
            out = []
            for ins in fn.instructions:
                if ins.op == "add" and len(ins.args) == 3 and all(x.lstrip("-").isdigit() for x in ins.args[1:]):
                    out.append(IRInstruction("const", (ins.args[0], str(int(ins.args[1]) + int(ins.args[2])))))
                    folded += 1
                else:
                    out.append(ins)
            fn.instructions = out
        return folded
