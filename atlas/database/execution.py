from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


Row = tuple[object, ...]


@dataclass(frozen=True)
class Column:
    name: str
    index: int


@dataclass(frozen=True)
class Predicate:
    column: int
    operator: str
    value: object

    def matches(self, row: Sequence[object]) -> bool:
        actual = row[self.column]
        if self.operator == "=":
            return actual == self.value
        if self.operator == "!=":
            return actual != self.value
        if self.operator == "<":
            return actual < self.value
        if self.operator == "<=":
            return actual <= self.value
        if self.operator == ">":
            return actual > self.value
        if self.operator == ">=":
            return actual >= self.value
        raise ValueError(f"unsupported predicate operator: {self.operator}")


class TableScan:
    def __init__(self, rows: Iterable[Sequence[object]]):
        self.rows = [tuple(row) for row in rows]

    def execute(self) -> list[Row]:
        return list(self.rows)


class FilterExec:
    def __init__(self, child: TableScan | "FilterExec", predicate: Predicate):
        self.child = child
        self.predicate = predicate

    def execute(self) -> list[Row]:
        return [row for row in self.child.execute() if self.predicate.matches(row)]


class ProjectExec:
    def __init__(self, child: TableScan | FilterExec | "ProjectExec", columns: Sequence[int]):
        self.child = child
        self.columns = tuple(columns)

    def execute(self) -> list[Row]:
        return [tuple(row[i] for i in self.columns) for row in self.child.execute()]


class HashJoinExec:
    def __init__(self, left: TableScan | FilterExec | ProjectExec, right: TableScan | FilterExec | ProjectExec,
                 left_key: int, right_key: int):
        self.left = left
        self.right = right
        self.left_key = left_key
        self.right_key = right_key

    def execute(self) -> list[Row]:
        buckets: dict[object, list[Row]] = {}
        for row in self.right.execute():
            buckets.setdefault(row[self.right_key], []).append(row)
        output: list[Row] = []
        for left_row in self.left.execute():
            for right_row in buckets.get(left_row[self.left_key], ()):
                output.append(left_row + right_row)
        return output


class ExecutionEngine:
    def scan(self, rows: Iterable[Sequence[object]]) -> TableScan:
        return TableScan(rows)

    def filter(self, child, column: int, operator: str, value: object) -> FilterExec:
        return FilterExec(child, Predicate(column, operator, value))

    def project(self, child, columns: Sequence[int]) -> ProjectExec:
        return ProjectExec(child, columns)

    def hash_join(self, left, right, left_key: int, right_key: int) -> HashJoinExec:
        return HashJoinExec(left, right, left_key, right_key)

    def run(self, plan) -> list[Row]:
        return plan.execute()
