from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

@dataclass(frozen=True)
class SSAInstruction:
    op: str
    result: str | None
    args: tuple[str, ...] = ()

@dataclass
class BasicBlock:
    name: str
    instructions: list[SSAInstruction] = field(default_factory=list)
    successors: set[str] = field(default_factory=set)
    predecessors: set[str] = field(default_factory=set)

@dataclass
class SSAFunction:
    name: str
    entry: str
    blocks: dict[str, BasicBlock]
    value_versions: dict[str, int] = field(default_factory=dict)

    def fresh(self, variable: str) -> str:
        version = self.value_versions.get(variable, 0)
        self.value_versions[variable] = version + 1
        return f"{variable}.{version}"

    def add_block(self, name: str) -> BasicBlock:
        if name in self.blocks:
            raise ValueError("block already exists")
        block = BasicBlock(name)
        self.blocks[name] = block
        return block
    def connect(self, source: str, target: str) -> None:
        self.blocks[source].successors.add(target)
        self.blocks[target].predecessors.add(source)

    def assign(self, block: str, variable: str, *operands: str) -> str:
        value = self.fresh(variable)
        self.blocks[block].instructions.append(
            SSAInstruction("assign", value, tuple(operands))
        )
        return value

    def phi(self, block: str, variable: str, operands: Iterable[str]) -> str:
        value = self.fresh(variable)
        incoming = tuple(operands)
        if len(incoming) != len(self.blocks[block].predecessors):
            raise ValueError("phi operand count must match predecessor count")
        self.blocks[block].instructions.append(SSAInstruction("phi", value, incoming))
        return value

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.entry not in self.blocks:
            errors.append("missing entry block")
            return errors
        for name, block in self.blocks.items():
            for successor in block.successors:
                if name not in self.blocks[successor].predecessors:
                    errors.append(f"missing predecessor edge {name}->{successor}")
            for predecessor in block.predecessors:
                if name not in self.blocks[predecessor].successors:
                    errors.append(f"missing successor edge {predecessor}->{name}")
            for ins in block.instructions:
                if ins.op == "phi" and len(ins.args) != len(block.predecessors):
                    errors.append(f"invalid phi in {name}")
        return errors

def compute_dominators(fn: SSAFunction) -> dict[str, set[str]]:
    all_blocks = set(fn.blocks)
    dom = {name: set(all_blocks) for name in all_blocks}
    dom[fn.entry] = {fn.entry}
    changed = True
    while changed:
        changed = False
        for name, block in fn.blocks.items():
            if name == fn.entry:
                continue
            if not block.predecessors:
                new_dom = {name}
            else:
                new_dom = {name} | set.intersection(*(dom[p] for p in block.predecessors))
            if new_dom != dom[name]:
                dom[name] = new_dom
                changed = True
    return dom
def dominance_frontier(fn: SSAFunction, dominators: dict[str, set[str]]) -> dict[str, set[str]]:
    frontier = {name: set() for name in fn.blocks}
    for name, block in fn.blocks.items():
        if len(block.predecessors) < 2:
            continue
        for predecessor in block.predecessors:
            runner = predecessor
            while runner not in dominators[name]:
                frontier[runner].add(name)
                parent_candidates = fn.blocks[runner].predecessors
                if not parent_candidates:
                    break
                runner = min(parent_candidates, key=lambda x: len(dominators[x]))
    return frontier
