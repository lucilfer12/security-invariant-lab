from __future__ import annotations

from dataclasses import dataclass, field

@dataclass(frozen=True)
class TableStats:
    rows: int
    distinct: dict[str, int] = field(default_factory=dict)

@dataclass(frozen=True)
class Scan:
    table: str

@dataclass(frozen=True)
class Filter:
    child: object
    column: str
    value: str

@dataclass(frozen=True)
class IndexLookup:
    table: str
    index: str
    value: str

@dataclass(frozen=True)
class Project:
    child: object
    columns: tuple[str, ...]

@dataclass(frozen=True)
class Plan:
    operator: object
    estimated_rows: float
    estimated_cost: float

class QueryPlanner:
    """Small cost-based logical planner choosing index lookup when statistics justify it."""
    def __init__(self, stats: dict[str, TableStats], indexes: dict[str, set[str]] | None = None):
        self.stats = stats
        self.indexes = indexes or {}

    def estimate_filter(self, table: str, column: str, value: str) -> float:
        stat = self.stats[table]
        distinct = max(1, stat.distinct.get(column, stat.rows))
        return max(1.0, stat.rows / distinct)

    def plan(self, table: str, column: str | None = None, value: str | None = None) -> Plan:
        stat = self.stats[table]
        if column is not None and value is not None and column in self.indexes.get(table, set()):
            rows = self.estimate_filter(table, column, value)
            return Plan(IndexLookup(table, column, value), rows, 1.0 + rows * 0.01)
        scan = Scan(table)
        if column is None or value is None:
            return Plan(scan, float(stat.rows), max(1.0, stat.rows))
        rows = self.estimate_filter(table, column, value)
        return Plan(Filter(scan, column, value), rows, stat.rows + rows)

    def project(self, plan: Plan, columns: tuple[str, ...]) -> Plan:
        if not columns:
            raise ValueError("projection cannot be empty")
        return Plan(Project(plan.operator, columns), plan.estimated_rows, plan.estimated_cost + len(columns))
