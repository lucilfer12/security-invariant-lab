from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

@dataclass(frozen=True)
class GeminiConfig:
    api_key: str | None = None
    model: str | None = None
    timeout: int = 45
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"

    @classmethod
    def from_env(cls) -> "GeminiConfig":
        return cls(
            api_key=os.getenv("GEMINI_API_KEY"),
            model=os.getenv("GEMINI_MODEL", "gemini-3.8-flash"),
            timeout=int(os.getenv("GEMINI_TIMEOUT", "45")),
        )

class GeminiClient:
    def __init__(self, config: GeminiConfig | None = None):
        self.config = config or GeminiConfig.from_env()

    @property
    def enabled(self) -> bool:
        return bool(self.config.api_key)

    def _url(self, model: str) -> str:
        key = self.config.api_key or ""
        return f"{self.config.base_url}/models/{model}:generateContent?key={key}"
    def generate(self, prompt: str, *, model: str | None = None) -> str:
        if not self.enabled:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        model = model or self.config.model or "gemini-3.8-flash"
        body = json.dumps({
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.15},
        }).encode()
        request = urllib.request.Request(
            self._url(model),
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Gemini HTTP {exc.code}: {detail[:800]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Gemini connection failed: {exc.reason}") from exc
        try:
            return payload["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Gemini response did not contain text") from exc
    def analyze_scan(self, scan: dict) -> str:
        prompt = (
            "You are a security research copilot. Analyze this static scan as hypotheses, "
            "not verdicts. Identify the highest-value properties to verify, suspicious data/control "
            "flows, and concrete local tests. Never invent evidence. Return structured sections.\n\n"
            + json.dumps(scan, indent=2)[:120000]
        )
        return self.generate(prompt)

def ai_report(scan: dict) -> dict:
    client = GeminiClient()
    if not client.enabled:
        return {"enabled": False, "message": "Set GEMINI_API_KEY to enable AI analysis."}
    try:
        return {"enabled": True, "model": client.config.model, "analysis": client.analyze_scan(scan)}
    except RuntimeError as exc:
        return {"enabled": True, "model": client.config.model, "error": str(exc)}
