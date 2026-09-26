from __future__ import annotations

from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Query:
    kind: str
    table: str
    columns: tuple[str, ...] = ()
    values: tuple[str, ...] = ()

def parse_sql(sql: str) -> Query:
    s = sql.strip().rstrip(";")
    if m := re.fullmatch(r"INSERT INTO (\w+) VALUES \(([^)]*)\)", s, re.I):
        return Query("insert", m.group(1), values=tuple(x.strip().strip("'") for x in m.group(2).split(",")))
    if m := re.fullmatch(r"SELECT (\*|[\w, ]+) FROM (\w+)", s, re.I):
        cols = ("*",) if m.group(1) == "*" else tuple(x.strip() for x in m.group(1).split(","))
        return Query("select", m.group(2), columns=cols)
    if m := re.fullmatch(r"DELETE FROM (\w+)", s, re.I):
        return Query("delete", m.group(1))
    raise ValueError("unsupported SQL")

class SQLDatabase:
    def __init__(self):
        self.tables: dict[str, list[tuple[str, ...]]] = {}

    def create_table(self, name: str) -> None:
        self.tables.setdefault(name, [])

    def execute(self, query: Query) -> list[tuple[str, ...]]:
        rows = self.tables.setdefault(query.table, [])
        if query.kind == "insert":
            rows.append(query.values); return []
        if query.kind == "select": return list(rows)
        if query.kind == "delete":
            count = len(rows); rows.clear(); return [(str(count),)]
        raise ValueError(query.kind)
