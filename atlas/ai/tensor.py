from __future__ import annotations

from dataclasses import dataclass
import math

class TensorError(ValueError):
    pass

@dataclass
class Tensor:
    shape: tuple[int, ...]
    values: list[float]

    def __post_init__(self):
        size = math.prod(self.shape)
        if size != len(self.values):
            raise TensorError("shape does not match value count")

    @classmethod
    def zeros(cls, shape: tuple[int, ...]) -> "Tensor":
        return cls(shape, [0.0] * math.prod(shape))

    def map(self, fn) -> "Tensor":
        return Tensor(self.shape, [fn(x) for x in self.values])

    def add(self, other: "Tensor") -> "Tensor":
        if self.shape != other.shape:
            raise TensorError("shape mismatch")
        return Tensor(self.shape, [a + b for a, b in zip(self.values, other.values)])

    def matmul2d(self, other: "Tensor") -> "Tensor":
        if len(self.shape) != 2 or len(other.shape) != 2 or self.shape[1] != other.shape[0]:
            raise TensorError("matmul requires compatible rank-2 tensors")
        m, k = self.shape
        _, n = other.shape
        out = []
        for i in range(m):
            for j in range(n):
                out.append(sum(self.values[i * k + t] * other.values[t * n + j] for t in range(k)))
        return Tensor((m, n), out)

@dataclass(frozen=True)
class Int8Quantized:
    scale: float
    zero_point: int
    values: tuple[int, ...]

    def dequantize(self) -> list[float]:
        return [(q - self.zero_point) * self.scale for q in self.values]

def quantize_int8(values: list[float]) -> Int8Quantized:
    if not values:
        raise TensorError("cannot quantize empty tensor")
    lo, hi = min(values), max(values)
    if hi == lo:
        return Int8Quantized(1.0, 0, tuple(0 for _ in values))
    scale = (hi - lo) / 255.0
    zero = round(-lo / scale - 128)
    quantized = tuple(max(-128, min(127, round(v / scale + zero))) for v in values)
    return Int8Quantized(scale, zero, quantized)
@dataclass
class KVCache:
    max_tokens: int
    keys: list[Tensor]
    values: list[Tensor]

    def __init__(self, max_tokens: int):
        if max_tokens <= 0:
            raise TensorError("max_tokens must be positive")
        self.max_tokens = max_tokens
        self.keys, self.values = [], []

    def append(self, key: Tensor, value: Tensor) -> None:
        if len(self.keys) >= self.max_tokens:
            raise TensorError("KV cache capacity exceeded")
        self.keys.append(key)
        self.values.append(value)

    def truncate(self, tokens: int) -> None:
        if tokens < 0:
            raise TensorError("tokens cannot be negative")
        self.keys = self.keys[:-tokens] if tokens else self.keys
        self.values = self.values[:-tokens] if tokens else self.values

    def __len__(self) -> int:
        return len(self.keys)
class DynamicBatcher:
    def __init__(self, max_batch: int):
        if max_batch <= 0:
            raise ValueError("max_batch must be positive")
        self.max_batch = max_batch
        self.pending: list[object] = []

    def submit(self, request: object) -> None:
        self.pending.append(request)

    def pop_batch(self) -> list[object]:
        batch = self.pending[:self.max_batch]
        del self.pending[:len(batch)]
        return batch

    def __len__(self) -> int:
        return len(self.pending)
