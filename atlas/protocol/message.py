from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

@dataclass(frozen=True)
class Message:
    version: int
    kind: str
    message_id: str
    payload: dict

    def canonical(self) -> bytes:
        body = {"v": self.version, "k": self.kind, "id": self.message_id, "p": self.payload}
        return json.dumps(body, sort_keys=True, separators=(",", ":")).encode()

    def digest(self) -> str:
        return hashlib.sha256(self.canonical()).hexdigest()

def encode_message(message: Message) -> bytes:
    return message.canonical()

def decode_message(data: bytes) -> Message:
    obj = json.loads(data.decode())
    return Message(int(obj["v"]), str(obj["k"]), str(obj["id"]), dict(obj["p"]))
