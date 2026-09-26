from dataclasses import dataclass


class TypeErrorATLASError(ValueError):
    pass


@dataclass(frozen=True)
class Type:
    name: str


INT = Type("int")
BOOL = Type("bool")


def infer_literal(value):
    if isinstance(value, bool):
        return BOOL
    if isinstance(value, int):
        return INT
    raise TypeErrorATLASError(f"unsupported literal type: {type(value).__name__}")


class TypeChecker:
    def __init__(self):
        self.env = {}

    def bind(self, name: str, typ: Type):
        self.env[name] = typ

    def check_binary(self, op: str, left: Type, right: Type) -> Type:
        if op in {"+", "-", "*", "/"} and left == right == INT:
            return INT
        if op in {"==", "!="} and left == right:
            return BOOL
        raise TypeErrorATLASError(f"invalid operands for {op}: {left.name}, {right.name}")
