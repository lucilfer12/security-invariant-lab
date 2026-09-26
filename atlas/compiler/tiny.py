from __future__ import annotations

from .ir import IRFunction, IRModule

def compile_expr(name: str, params: tuple[str, ...], expression: str) -> IRModule:
    tokens = expression.replace("+", " + ").replace("*", " * ").split()
    if not tokens or len(tokens) % 2 == 0:
        raise ValueError("malformed expression")
    output, ops = [], []
    precedence = {"+": 1, "*": 2}
    for token in tokens:
        if token in precedence:
            while ops and precedence[ops[-1]] >= precedence[token]:
                output.append(ops.pop())
            ops.append(token)
        else:
            output.append(token)
    output.extend(reversed(ops))
    fn, stack, temp = IRFunction(name, params), [], 0
    for token in output:
        if token in precedence:
            if len(stack) < 2:
                raise ValueError("malformed expression")
            b, a = stack.pop(), stack.pop()
            target = f"%t{temp}"; temp += 1
            fn.emit("add" if token == "+" else "mul", target, a, b)
            stack.append(target)
        else:
            op = "const" if token.lstrip("-").isdigit() else "load"
            fn.emit(op, token)
            stack.append(token)
    if len(stack) != 1:
        raise ValueError("malformed expression")
    fn.emit("return", stack[0])
    return IRModule({name: fn})
