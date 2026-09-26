class GCounter:
    """Grow-only counter for monotonic replicated aggregation."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self._values = {node_id: 0}

    def increment(self, amount: int = 1):
        if amount < 0:
            raise ValueError("GCounter cannot decrement")
        self._values[self.node_id] = self._values.get(self.node_id, 0) + amount

    def merge(self, other: "GCounter"):
        for node, value in other._values.items():
            self._values[node] = max(self._values.get(node, 0), value)

    @property
    def value(self):
        return sum(self._values.values())

    def state(self):
        return dict(sorted(self._values.items()))


class LWWRegister:
    """Last-writer-wins register with deterministic node-id tie breaking."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self._value = None
        self._timestamp = -1
        self._writer = ""

    def assign(self, value, timestamp: int):
        candidate = (timestamp, self.node_id)
        current = (self._timestamp, self._writer)
        if candidate >= current:
            self._value, self._timestamp, self._writer = value, timestamp, self.node_id

    def merge(self, other: "LWWRegister"):
        if (other._timestamp, other._writer) > (self._timestamp, self._writer):
            self._value = other._value
            self._timestamp = other._timestamp
            self._writer = other._writer

    @property
    def value(self):
        return self._value
