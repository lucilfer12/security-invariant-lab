from __future__ import annotations

import json
import re
import hashlib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

@dataclass(frozen=True)
class WebFinding:
    id: str
    kind: str
    title: str
    confidence: str
    evidence: str
    recommendation: str

def inspect_headers(headers: dict[str, str]) -> list[WebFinding]:
    lower = {k.lower(): v for k, v in headers.items()}
    out: list[WebFinding] = []
    def add(kind, title, confidence, evidence, recommendation):
        import hashlib
        fid = "WEB-" + hashlib.sha1((kind + title + evidence).encode()).hexdigest()[:10].upper()
        out.append(WebFinding(fid, kind, title, confidence, evidence, recommendation))

    if "content-security-policy" not in lower:
        add("headers", "Content-Security-Policy header not observed", "low",
            "CSP header absent from supplied response headers",
            "Define a policy appropriate to the application and test it in authorized environments.")
    if "strict-transport-security" not in lower:
        add("headers", "HSTS header not observed", "low",
            "Strict-Transport-Security header absent",
            "Use HSTS where HTTPS-only transport is an intended security boundary.")
    set_cookie = lower.get("set-cookie", "")
    if set_cookie:
        for flag in ("Secure", "HttpOnly", "SameSite"):
            if flag.lower() not in set_cookie.lower():
                add("cookie", f"{flag} cookie attribute not observed", "low",
                    set_cookie[:500],
                    f"Review whether the {flag} attribute is appropriate for session or sensitive cookies.")
    return out

def inspect_openapi(path: str | Path) -> list[WebFinding]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out: list[WebFinding] = []
    paths = data.get("paths", {})
    security_defaults = data.get("security")
    for route, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, operation in item.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "head", "options"}:
                continue
            if isinstance(operation, dict) and "security" not in operation and security_defaults is None:
                out.append(WebFinding(
                    f"API-{hashlib.sha1((route + method).encode()).hexdigest()[:10].upper()}",
                    "api-auth",
                    f"No declared OpenAPI security requirement for {method.upper()} {route}",
                    "low",
                    f"{method.upper()} {route}",
                    "Verify whether authentication/authorization is intentionally absent and test the actual policy.",
                ))
            if "parameters" in operation:
                for param in operation["parameters"]:
                    if isinstance(param, dict) and param.get("in") == "query" and param.get("required") is True:
                        schema = param.get("schema", {})
                        if schema.get("type") == "string" and "maxLength" not in schema:
                            out.append(WebFinding(
                                f"API-{abs(hash(route + method + param.get('name',''))) % 10**10:010d}",
                                "input-validation",
                                f"Required string parameter without declared maxLength: {param.get('name','')}",
                                "low",
                                f"{method.upper()} {route} parameter={param.get('name','')}",
                                "Bound inputs explicitly where resource exhaustion or storage growth is a concern.",
                            ))
    return out

def inspect_url(url: str) -> dict:
    parsed = urlparse(url)
    return {
        "scheme": parsed.scheme,
        "hostname": parsed.hostname,
        "port": parsed.port,
        "path": parsed.path or "/",
        "local_only": parsed.hostname in {"127.0.0.1", "localhost", "::1"},
    }

__all__ = ["WebFinding", "inspect_headers", "inspect_openapi", "inspect_url"]
