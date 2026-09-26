from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .types import FindingRecord, ScanResult

class AnalyzerPlugin(Protocol):
    name: str
    def analyze(self, result: ScanResult) -> list[FindingRecord]: ...

@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    description: str
    capabilities: tuple[str, ...]
    api_version: str = "1"

class PluginManager:
    def __init__(self) -> None:
        self._plugins: dict[str, AnalyzerPlugin] = {}

    def register(self, plugin: AnalyzerPlugin) -> PluginManifest:
        if plugin.name in self._plugins:
            raise ValueError(f"plugin already registered: {plugin.name}")
        self._plugins[plugin.name] = plugin
        return PluginManifest(plugin.name, "0.1", plugin.__class__.__doc__ or "", ("analyzer",))

    def analyze(self, result: ScanResult) -> list[FindingRecord]:
        findings: list[FindingRecord] = []
        for name in sorted(self._plugins):
            findings.extend(self._plugins[name].analyze(result))
        return findings
