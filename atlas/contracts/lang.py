from __future__ import annotations

from dataclasses import dataclass, field
import re

class ContractSyntaxError(ValueError):
    pass

@dataclass(frozen=True)
class Field:
    name: str
    type: str
    owned: bool = False

@dataclass(frozen=True)
class Function:
    name: str
    params: tuple[str, ...]
    requires: tuple[str, ...] = ()
    moves: tuple[str, ...] = ()
    returns: str | None = None

@dataclass
class ContractModule:
    name: str
    resources: dict[str, tuple[Field, ...]] = field(default_factory=dict)
    functions: dict[str, Function] = field(default_factory=dict)

_TOKEN = re.compile(r"\s*(?:(\d+)|([A-Za-z_][A-Za-z0-9_]*)|(:|\{|\}|\(|\)|,|;|->))")

class ContractParser:
    """Ownership/resource contract language front-end with semantic checks."""
    def parse(self, source: str) -> ContractModule:
        tokens = [m.group(1) or m.group(2) or m.group(3) for m in _TOKEN.finditer(source)]
        if not tokens:
            raise ContractSyntaxError("empty contract")
        pos = 0
        if tokens[pos] != "contract":
            raise ContractSyntaxError("expected 'contract'")
        pos += 1
        name = tokens[pos]; pos += 1
        module = ContractModule(name)
        while pos < len(tokens):
            kind = tokens[pos]; pos += 1
            if kind == "resource":
                pos = self._resource(tokens, pos, module)
            elif kind == "fn":
                pos = self._function(tokens, pos, module)
            else:
                raise ContractSyntaxError(f"unexpected token {kind!r}")
        self.validate(module)
        return module
    def _resource(self, tokens, pos, module):
        name = tokens[pos]; pos += 1
        if tokens[pos] != "{":
            raise ContractSyntaxError("expected '{' after resource")
        pos += 1
        fields = []
        while tokens[pos] != "}":
            owned = tokens[pos] == "owned"
            if owned:
                pos += 1
            field_name = tokens[pos]; pos += 1
            if tokens[pos] != ":":
                raise ContractSyntaxError("expected ':' in field")
            pos += 1
            field_type = tokens[pos]; pos += 1
            if tokens[pos] == ";":
                pos += 1
            fields.append(Field(field_name, field_type, owned))
        pos += 1
        module.resources[name] = tuple(fields)
        return pos

    def _function(self, tokens, pos, module):
        name = tokens[pos]; pos += 1
        if tokens[pos] != "(":
            raise ContractSyntaxError("expected '('")
        pos += 1
        params = []
        while tokens[pos] != ")":
            params.append(tokens[pos]); pos += 1
            if tokens[pos] != ",":
                if tokens[pos] != ")":
                    raise ContractSyntaxError("expected ',' or ')'")
                break
            pos += 1
        pos += 1
        requires, moves = [], []
        returns = None
        while pos < len(tokens) and tokens[pos] not in ("fn", "resource"):
            if tokens[pos] == "requires":
                pos += 1; requires.append(tokens[pos]); pos += 1
            elif tokens[pos] == "move":
                pos += 1; moves.append(tokens[pos]); pos += 1
            elif tokens[pos] == "->":
                pos += 1; returns = tokens[pos]; pos += 1
            elif tokens[pos] == ";":
                pos += 1
            else:
                raise ContractSyntaxError(f"unexpected function token {tokens[pos]!r}")
        if name in module.functions:
            raise ContractSyntaxError(f"duplicate function {name}")
        module.functions[name] = Function(name, tuple(params), tuple(requires), tuple(moves), returns)
        return pos

    @staticmethod
    def validate(module: ContractModule) -> None:
        resources = set(module.resources)
        for fn in module.functions.values():
            if len(set(fn.moves)) != len(fn.moves):
                raise ContractSyntaxError(f"duplicate move in {fn.name}")
            for moved in fn.moves:
                if moved not in resources:
                    raise ContractSyntaxError(f"cannot move unknown resource {moved}")
