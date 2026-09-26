from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import asdict
from urllib.parse import urlparse

from .passive import inspect_headers, inspect_url

def probe(url: str, timeout: int = 5, max_bytes: int = 1_000_000) -> dict:
    meta = inspect_url(url)
    if not meta["local_only"]:
        raise ValueError("localhost-only probe: use 127.0.0.1, localhost, or ::1")
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "SIL-Passive/0.5"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(max_bytes)
            headers = dict(response.headers.items())
            findings = inspect_headers(headers)
            return {
                "url": url,
                "status": response.status,
                "headers": headers,
                "body_bytes": len(body),
                "findings": [asdict(f) for f in findings],
                "local_only": True,
            }
    except urllib.error.HTTPError as exc:
        headers = dict(exc.headers.items())
        return {
            "url": url,
            "status": exc.code,
            "headers": headers,
            "body_bytes": 0,
            "findings": [asdict(f) for f in inspect_headers(headers)],
            "local_only": True,
        }
