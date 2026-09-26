from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hmac
import hashlib

class TLSState(str, Enum):
    INITIAL = "initial"
    CLIENT_HELLO = "client-hello"
    SERVER_HELLO = "server-hello"
    ESTABLISHED = "established"
    CLOSED = "closed"

@dataclass
class TLS13Session:
    state: TLSState = TLSState.INITIAL
    transcript: list[bytes] = None

    def __post_init__(self):
        self.transcript = [] if self.transcript is None else list(self.transcript)

    def client_hello(self, payload: bytes) -> None:
        if self.state is not TLSState.INITIAL:
            raise RuntimeError("invalid ClientHello transition")
        self.transcript.append(payload)
        self.state = TLSState.CLIENT_HELLO

    def server_hello(self, payload: bytes) -> None:
        if self.state is not TLSState.CLIENT_HELLO:
            raise RuntimeError("invalid ServerHello transition")
        self.transcript.append(payload)
        self.state = TLSState.ESTABLISHED

    def close(self) -> None:
        self.state = TLSState.CLOSED

    def transcript_hash(self) -> bytes:
        return hashlib.sha256(b"".join(self.transcript)).digest()

@dataclass
class QUICConnection:
    connection_id: bytes
    packet_number: int = 0
    bytes_in_flight: int = 0
    max_data: int = 65536
    closed: bool = False

    def send(self, payload: bytes) -> int:
        if self.closed:
            raise RuntimeError("connection closed")
        if not payload:
            raise ValueError("empty payload")
        if self.bytes_in_flight + len(payload) > self.max_data:
            raise RuntimeError("flow control limit exceeded")
        self.packet_number += 1
        self.bytes_in_flight += len(payload)
        return self.packet_number

    def ack(self, size: int) -> None:
        if size < 0:
            raise ValueError("negative acknowledgment")
        self.bytes_in_flight = max(0, self.bytes_in_flight - size)

    def close(self) -> None:
        self.closed = True

def stateless_reset_token(secret: bytes, connection_id: bytes) -> bytes:
    if not secret or not connection_id:
        raise ValueError("secret and connection id are required")
    return hmac.new(secret, connection_id, hashlib.sha256).digest()[:16]
