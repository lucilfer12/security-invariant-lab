from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

class PBFTPhase(str, Enum):
    PRE_PREPARE = "pre-prepare"
    PREPARE = "prepare"
    COMMIT = "commit"
    DECIDED = "decided"

@dataclass(frozen=True)
class Proposal:
    view: int
    sequence: int
    digest: str
    proposer: str

@dataclass(frozen=True)
class Vote:
    phase: PBFTPhase
    view: int
    sequence: int
    digest: str
    validator: str

@dataclass
class ConsensusInstance:
    proposal: Proposal
    prepares: set[str] = field(default_factory=set)
    commits: set[str] = field(default_factory=set)
    phase: PBFTPhase = PBFTPhase.PRE_PREPARE

class PBFTNode:
    """Deterministic PBFT quorum tracker for 3f+1 validator sets."""
    def __init__(self, node_id: str, validators: set[str], max_faults: int):
        if node_id not in validators:
            raise ValueError("node must be a validator")
        if len(validators) < 3 * max_faults + 1:
            raise ValueError("validator set must contain at least 3f+1 nodes")
        self.node_id = node_id
        self.validators = frozenset(validators)
        self.max_faults = max_faults
        self.instances: dict[tuple[int, int], ConsensusInstance] = {}
        self.commit_history: list[str] = []

    @property
    def prepare_quorum(self) -> int:
        return 2 * self.max_faults

    @property
    def commit_quorum(self) -> int:
        return 2 * self.max_faults + 1
    @staticmethod
    def digest_request(request: dict) -> str:
        raw = json.dumps(request, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()

    def propose(self, view: int, sequence: int, request: dict) -> Proposal:
        key = (view, sequence)
        if key in self.instances:
            raise ValueError("consensus instance already exists")
        proposal = Proposal(view, sequence, self.digest_request(request), self.node_id)
        self.instances[key] = ConsensusInstance(proposal)
        return proposal

    def accept_prepare(self, vote: Vote) -> bool:
        instance = self.instances.get((vote.view, vote.sequence))
        if instance is None or vote.phase is not PBFTPhase.PREPARE:
            return False
        if vote.digest != instance.proposal.digest or vote.validator not in self.validators:
            return False
        instance.prepares.add(vote.validator)
        if len(instance.prepares) >= self.prepare_quorum:
            instance.phase = PBFTPhase.PREPARE
        return True

    def accept_commit(self, vote: Vote) -> bool:
        instance = self.instances.get((vote.view, vote.sequence))
        if instance is None or vote.phase is not PBFTPhase.COMMIT:
            return False
        if vote.digest != instance.proposal.digest or vote.validator not in self.validators:
            return False
        instance.commits.add(vote.validator)
        if len(instance.commits) >= self.commit_quorum:
            instance.phase = PBFTPhase.DECIDED
            if vote.digest not in self.commit_history:
                self.commit_history.append(vote.digest)
        else:
            instance.phase = PBFTPhase.COMMIT
        return True

    def decided(self, view: int, sequence: int) -> bool:
        instance = self.instances.get((view, sequence))
        return instance is not None and instance.phase is PBFTPhase.DECIDED
