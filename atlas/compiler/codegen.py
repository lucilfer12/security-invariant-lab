from __future__ import annotations

from .bytecode import Instruction
from .ir import IRFunction


class BytecodeCompiler:
    """Lower the small ATLAS IR into stack bytecode without mutating the IR."""

    def compile_function(self, function: IRFunction) -> list[Instruction]:
        code: list[Instruction] = []
        for ins in function.instructions:
            if ins.op == "const":
                if len(ins.args) == 1:
                    code.append(Instruction("PUSH", int(ins.args[0])))
                elif len(ins.args) == 2:
                    code.append(Instruction("PUSH", int(ins.args[1])))
                else:
                    raise ValueError("const expects one or two operands")
            elif ins.op == "load":
                if len(ins.args) != 1:
                    raise ValueError("load expects one operand")
                code.append(Instruction("LOAD", ins.args[0]))
            elif ins.op in {"add", "mul"}:
                code.append(Instruction(ins.op.upper()))
            elif ins.op == "return":
                code.append(Instruction("HALT"))
            else:
                raise ValueError(f"unsupported IR opcode: {ins.op}")
        if not code or code[-1].op != "HALT":
            code.append(Instruction("HALT"))
        return code
