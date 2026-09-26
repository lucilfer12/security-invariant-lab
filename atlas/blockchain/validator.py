from __future__ import annotations

from dataclasses import dataclass
from .state import StateMachine, StateError, Transfer

@dataclass(frozen=True)
class ValidatorConfig:
    chain_id: int
    min_gas: int = 21_000

@dataclass(frozen=True)
class SignedTransfer:
    tx: Transfer
    gas_limit: int
    chain_id: int
    signature_valid: bool

class Validator:
    """Consensus-adjacent transaction admission and deterministic state application."""
    def __init__(self, config: ValidatorConfig, state: StateMachine | None = None):
        self.config = config
        self.state = state or StateMachine()

    def validate_tx(self, signed: SignedTransfer) -> None:
        if signed.chain_id != self.config.chain_id:
            raise StateError("wrong chain id")
        if not signed.signature_valid:
            raise StateError("invalid signature")
        if signed.gas_limit < self.config.min_gas:
            raise StateError("gas limit below minimum")
        self.state.validate(signed.tx)

    def apply_block(self, txs: list[SignedTransfer]) -> int:
        for signed in txs:
            self.validate_tx(signed)
        for signed in txs:
            self.state.apply(signed.tx)
        return len(txs)

    def balance(self, address: str) -> int:
        return self.state.account(address).balance
