from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import time

@dataclass(frozen=True)
class Capability:
    subject: str
    action: str
    resource: str
    expires: int
    nonce: str

    def payload(self) -> bytes:
        return f"{self.subject}|{self.action}|{self.resource}|{self.expires}|{self.nonce}".encode()

class CapabilityAuthority:
    def __init__(self, secret: bytes):
        self.secret = secret

    def issue(self, capability: Capability) -> str:
        raw = capability.payload()
        sig = hmac.new(self.secret, raw, hashlib.sha256).hexdigest()
        return json.dumps({"c": raw.decode(), "s": sig}, separators=(",", ":"))

    def verify(self, token: str, subject: str, action: str, resource: str, now: int | None = None) -> bool:
        try:
            obj = json.loads(token)
            raw, sig = obj["c"].encode(), obj["s"]
            parts = raw.decode().split("|")
            expected = hmac.new(self.secret, raw, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected) or len(parts) != 5:
                return False
            sub, act, res, exp, _ = parts
            t = int(time.time()) if now is None else now
            return sub == subject and act in (action, "*") and res in (resource, "*") and t <= int(exp)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            return False
