from dataclasses import dataclass
from enum import Enum


class MemberState(str, Enum):
    ALIVE = "alive"
    SUSPECT = "suspect"
    DEAD = "dead"


@dataclass(frozen=True)
class Member:
    node_id: str
    incarnation: int = 0
    state: MemberState = MemberState.ALIVE


class Membership:
    """Deterministic SWIM-like membership table with incarnation ordering."""

    def __init__(self):
        self._members = {}

    def upsert(self, member: Member) -> bool:
        current = self._members.get(member.node_id)
        if current is None or member.incarnation > current.incarnation:
            self._members[member.node_id] = member
            return True
        if member.incarnation == current.incarnation and member.state != current.state:
            if member.state == MemberState.DEAD or current.state == MemberState.SUSPECT:
                self._members[member.node_id] = member
                return True
        return False

    def get(self, node_id: str):
        return self._members.get(node_id)

    def members(self, state=None):
        values = sorted(self._members.values(), key=lambda m: m.node_id)
        return [m for m in values if state is None or m.state == state]

    def digest(self) -> tuple:
        return tuple((m.node_id, m.incarnation, m.state.value) for m in self.members())
