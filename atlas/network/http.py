from __future__ import annotations

from dataclasses import dataclass

class HTTPError(ValueError):
    pass

@dataclass(frozen=True)
class HTTPRequest:
    method: str
    target: str
    version: str
    headers: tuple[tuple[str, str], ...]
    body: bytes

    def header(self, name: str) -> str | None:
        wanted = name.lower()
        for key, value in self.headers:
            if key.lower() == wanted:
                return value
        return None

def parse_request(raw: bytes) -> HTTPRequest:
    head, sep, body = raw.partition(b"\r\n\r\n")
    if not sep:
        raise HTTPError("request headers are incomplete")
    lines = head.split(b"\r\n")
    try:
        method, target, version = lines[0].decode("ascii").split(" ", 2)
    except ValueError as exc:
        raise HTTPError("invalid request line") from exc
    if not version.startswith("HTTP/"):
        raise HTTPError("invalid HTTP version")
    headers = []
    for line in lines[1:]:
        if b":" not in line:
            raise HTTPError("invalid header line")
        key, value = line.split(b":", 1)
        key = key.decode("latin1").strip()
        value = value.decode("latin1").strip()
        if not key or "\r" in value or "\n" in value:
            raise HTTPError("invalid header")
        headers.append((key, value))
    return HTTPRequest(method, target, version, tuple(headers), body)

def build_response(status: int, reason: str, body: bytes = b"",
                   headers: dict[str, str] | None = None) -> bytes:
    if not 100 <= status <= 999:
        raise HTTPError("invalid status")
    hdrs = dict(headers or {})
    hdrs.setdefault("Content-Length", str(len(body)))
    hdrs.setdefault("Connection", "close")
    lines = [f"HTTP/1.1 {status} {reason}"] + [f"{k}: {v}" for k,v in hdrs.items()]
    return "\r\n".join(lines).encode() + b"\r\n\r\n" + body
