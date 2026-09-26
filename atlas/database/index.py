from bisect import bisect_left


class BTreeIndex:
    """Deterministic in-memory ordered index reference implementation."""

    def __init__(self):
        self._keys = []
        self._values = {}

    def put(self, key, value):
        if key not in self._values:
            self._keys.insert(bisect_left(self._keys, key), key)
        self._values[key] = value

    def get(self, key):
        return self._values.get(key)

    def delete(self, key):
        if key in self._values:
            self._values.pop(key)
            self._keys.pop(bisect_left(self._keys, key))

    def range(self, start=None, end=None):
        lo = 0 if start is None else bisect_left(self._keys, start)
        hi = len(self._keys) if end is None else bisect_left(self._keys, end)
        return [(k, self._values[k]) for k in self._keys[lo:hi]]
