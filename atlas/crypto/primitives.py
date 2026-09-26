from __future__ import annotations

import hashlib
import hmac

def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()

def hmac_sha256(key: bytes, data: bytes) -> bytes:
    return hmac.new(key, data, hashlib.sha256).digest()

def hkdf_expand(prk: bytes, info: bytes, length: int) -> bytes:
    if length < 0 or length > 255 * hashlib.sha256().digest_size:
        raise ValueError("invalid HKDF length")
    out, previous = b"", b""
    for counter in range(1, 256):
        if len(out) >= length:
            break
        previous = hmac_sha256(prk, previous + info + bytes([counter]))
        out += previous
    return out[:length]
