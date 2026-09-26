from dataclasses import dataclass


@dataclass(frozen=True)
class Instruction:
    op: str
    arg: int | None = None


class BytecodeVerifier:
    STACK_EFFECT = {"PUSH": 1, "ADD": -1, "SUB": -1, "MUL": -1, "DIV": -1, "HALT": 0}

    def verify(self, code):
        depth = 0
        for pc, ins in enumerate(code):
            if ins.op not in self.STACK_EFFECT:
                raise ValueError(f"unknown opcode at {pc}: {ins.op}")
            if ins.op == "PUSH" and ins.arg is None:
                raise ValueError("PUSH requires an operand")
            depth += self.STACK_EFFECT[ins.op]
            if depth < 0:
                raise ValueError(f"stack underflow at {pc}")
        if not code or code[-1].op != "HALT":
            raise ValueError("bytecode must terminate with HALT")
        return True


class BytecodeVM:
    def run(self, code):
        BytecodeVerifier().verify(code)
        stack = []
        for ins in code:
            if ins.op == "PUSH":
                stack.append(ins.arg)
            elif ins.op in {"ADD", "SUB", "MUL", "DIV"}:
                b, a = stack.pop(), stack.pop()
                if ins.op == "ADD": stack.append(a + b)
                elif ins.op == "SUB": stack.append(a - b)
                elif ins.op == "MUL": stack.append(a * b)
                else:
                    if b == 0: raise ZeroDivisionError
                    stack.append(a // b)
            elif ins.op == "HALT":
                break
        return stack[-1] if stack else None
