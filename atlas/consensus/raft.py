from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

class NodeState(str, Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass(frozen=True)
class Entry:
    term: int
    index: int
    command: dict

class RaftNode:
    def __init__(self, node_id: str):
        self.id = node_id
        self.term = 0
        self.state = NodeState.FOLLOWER
        self.log: list[Entry] = []
        self.commit_index = -1
        self.votes: set[str] = set()

    def become_candidate(self) -> None:
        self.term += 1; self.state = NodeState.CANDIDATE; self.votes = {self.id}

    def become_leader(self) -> None:
        self.state = NodeState.LEADER

    def append(self, command: dict) -> Entry:
        if self.state != NodeState.LEADER:
            raise RuntimeError("only leader may append")
        entry = Entry(self.term, len(self.log), command)
        self.log.append(entry)
        return entry

    def commit(self, index: int) -> None:
        if not 0 <= index < len(self.log):
            raise IndexError(index)
        self.commit_index = max(self.commit_index, index)
