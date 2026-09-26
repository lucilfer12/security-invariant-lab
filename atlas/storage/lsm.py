from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import os
from threading import RLock

TOMBSTONE = None

@dataclass(frozen=True)
class VersionedValue:
    seq: int
    value: bytes | None

@dataclass(frozen=True)
class SSTable:
    level: int
    path: Path
    entries: int

class WriteAheadLog:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def append(self, seq: int, key: str, value: bytes | None) -> None:
        record = {"seq": seq, "key": key, "value": None if value is None else value.hex()}
        raw = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode()
        with self._lock, self.path.open("ab") as fh:
            fh.write(raw)
            fh.flush()
            os.fsync(fh.fileno())

    def replay(self) -> list[VersionedValue | tuple[int, str, bytes | None]]:
        out: list[tuple[int, str, bytes | None]] = []
        if not self.path.exists():
            return out
        for line in self.path.read_bytes().splitlines():
            if not line:
                continue
            record = json.loads(line)
            value = record["value"]
            out.append((int(record["seq"]), record["key"], None if value is None else bytes.fromhex(value)))
        return out
class MemTable:
    def __init__(self) -> None:
        self._data: dict[str, VersionedValue] = {}

    def put(self, seq: int, key: str, value: bytes) -> None:
        self._data[key] = VersionedValue(seq, value)

    def delete(self, seq: int, key: str) -> None:
        self._data[key] = VersionedValue(seq, TOMBSTONE)

    def items(self):
        return sorted(self._data.items())

    def __len__(self) -> int:
        return len(self._data)

class LSMEngine:
    """Small, durable LSM-style KV engine with WAL, immutable tables and compaction."""
    def __init__(self, root: str | Path, memtable_limit: int = 1024):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.wal = WriteAheadLog(self.root / "wal.log")
        self.memtable_limit = max(1, memtable_limit)
        self.memtable = MemTable()
        self._tables: list[SSTable] = []
        self._seq = 0
        self._lock = RLock()
        for seq, key, value in self.wal.replay():
            self._seq = max(self._seq, seq)
            if value is None:
                self.memtable.delete(seq, key)
            else:
                self.memtable.put(seq, key, value)
        self._discover_tables()
    def _discover_tables(self) -> None:
        tables: list[SSTable] = []
        for path in self.root.glob("sstable-*.jsonl"):
            try:
                level, _ = path.stem.removeprefix("sstable-").split("-", 1)
                entries = sum(1 for _ in path.open("rb"))
                tables.append(SSTable(int(level), path, entries))
            except (ValueError, OSError):
                continue
        self._tables = sorted(tables, key=lambda t: (t.level, t.path.name), reverse=True)
        for table in self._tables:
            parts = table.path.stem.split("-")
            if len(parts) >= 3:
                try:
                    self._seq = max(self._seq, int(parts[2]))
                except ValueError:
                    pass

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def put(self, key: str, value: bytes) -> int:
        if not key:
            raise ValueError("key cannot be empty")
        with self._lock:
            seq = self._next_seq()
            self.wal.append(seq, key, value)
            self.memtable.put(seq, key, value)
            if len(self.memtable) >= self.memtable_limit:
                self.flush()
            return seq

    def delete(self, key: str) -> int:
        with self._lock:
            seq = self._next_seq()
            self.wal.append(seq, key, None)
            self.memtable.delete(seq, key)
            if len(self.memtable) >= self.memtable_limit:
                self.flush()
            return seq

    def _read_table(self, table: SSTable) -> dict[str, VersionedValue]:
        result: dict[str, VersionedValue] = {}
        for line in table.path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            value = row["value"]
            result[row["key"]] = VersionedValue(
                int(row["seq"]), None if value is None else bytes.fromhex(value)
            )
        return result

    def get(self, key: str, snapshot: int | None = None) -> bytes | None:
        with self._lock:
            snap = self._seq if snapshot is None else snapshot
            candidates: list[VersionedValue] = []
            item = self.memtable._data.get(key)
            if item is not None and item.seq <= snap:
                candidates.append(item)
            for table in self._tables:
                item = self._read_table(table).get(key)
                if item is not None and item.seq <= snap:
                    candidates.append(item)
            if not candidates:
                return None
            winner = max(candidates, key=lambda x: x.seq)
            return winner.value
    def flush(self) -> SSTable | None:
        with self._lock:
            if not self.memtable:
                return None
            digest = hashlib.sha256(f"{self._seq}:{len(self.memtable)}".encode()).hexdigest()[:16]
            path = self.root / f"sstable-0-{self._seq}-{digest}.jsonl"
            with path.open("w", encoding="utf-8") as fh:
                for key, versioned in self.memtable.items():
                    fh.write(json.dumps({
                        "key": key,
                        "seq": versioned.seq,
                        "value": None if versioned.value is None else versioned.value.hex(),
                    }, sort_keys=True, separators=(",", ":")) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            table = SSTable(0, path, len(self.memtable))
            self._tables.insert(0, table)
            self.memtable = MemTable()
            self._truncate_wal()
            return table

    def _truncate_wal(self) -> None:
        tmp = self.wal.path.with_suffix(".tmp")
        tmp.write_bytes(b"")
        os.replace(tmp, self.wal.path)

    def compact(self) -> SSTable | None:
        with self._lock:
            self.flush()
            if len(self._tables) < 2:
                return self._tables[0] if self._tables else None
            merged: dict[str, VersionedValue] = {}
            for table in self._tables:
                for key, versioned in self._read_table(table).items():
                    current = merged.get(key)
                    if current is None or versioned.seq > current.seq:
                        merged[key] = versioned
            digest = hashlib.sha256(
                "|".join(f"{k}:{v.seq}" for k, v in sorted(merged.items())).encode()
            ).hexdigest()[:16]
            path = self.root / f"sstable-1-{self._seq}-{digest}.jsonl"
            with path.open("w", encoding="utf-8") as fh:
                for key, versioned in sorted(merged.items()):
                    fh.write(json.dumps({
                        "key": key, "seq": versioned.seq,
                        "value": None if versioned.value is None else versioned.value.hex()
                    }, sort_keys=True, separators=(",", ":")) + "\n")
                fh.flush()
                os.fsync(fh.fileno())
            old = list(self._tables)
            self._tables = [SSTable(1, path, len(merged))]
            for table in old:
                try:
                    table.path.unlink()
                except FileNotFoundError:
                    pass
            return self._tables[0]

    def snapshot(self) -> int:
        with self._lock:
            return self._seq
