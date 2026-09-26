from __future__ import annotations

from dataclasses import dataclass
from collections import defaultdict
from typing import Callable, Any

@dataclass(frozen=True)
class Model:
    name: str
    version: str
    handler: Callable[[list[Any]], list[Any]]

class ModelRegistry:
    def __init__(self):
        self.models: dict[str, Model] = {}

    def register(self, model: Model) -> None:
        self.models[f"{model.name}:{model.version}"] = model

    def get(self, name: str, version: str = "latest") -> Model:
        if version != "latest":
            return self.models[f"{name}:{version}"]
        candidates = [m for m in self.models.values() if m.name == name]
        if not candidates:
            raise KeyError(name)
        return sorted(candidates, key=lambda m: m.version)[-1]

class InferenceBatcher:
    def __init__(self, registry: ModelRegistry):
        self.registry = registry
        self.queues: dict[str, list[Any]] = defaultdict(list)

    def submit(self, name: str, item: Any) -> None:
        self.queues[name].append(item)

    def flush(self, name: str, version: str = "latest") -> list[Any]:
        items = self.queues.pop(name, [])
        return self.registry.get(name, version).handler(items)
