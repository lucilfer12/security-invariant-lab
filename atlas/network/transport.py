from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

class TCPState(str, Enum):
    CLOSED="CLOSED"; SYN_SENT="SYN_SENT"; ESTABLISHED="ESTABLISHED"; FIN_WAIT="FIN_WAIT"

@dataclass
class TCPSession:
    state: TCPState = TCPState.CLOSED
    send_seq: int = 0
    recv_seq: int = 0

    def connect(self) -> None:
        if self.state != TCPState.CLOSED: raise RuntimeError("invalid connect")
        self.state = TCPState.SYN_SENT

    def syn_ack(self) -> None:
        if self.state != TCPState.SYN_SENT: raise RuntimeError("invalid syn-ack")
        self.state = TCPState.ESTABLISHED

    def close(self) -> None:
        if self.state != TCPState.ESTABLISHED: raise RuntimeError("invalid close")
        self.state = TCPState.FIN_WAIT

    def ack_close(self) -> None:
        if self.state != TCPState.FIN_WAIT: raise RuntimeError("invalid close ack")
        self.state = TCPState.CLOSED
