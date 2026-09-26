from __future__ import annotations

from dataclasses import dataclass

class DriverError(RuntimeError):
    pass

@dataclass
class BlockDevice:
    name: str
    sectors: int
    sector_size: int = 512

    def __post_init__(self):
        if self.sectors <= 0 or self.sector_size <= 0:
            raise ValueError("invalid block device geometry")
        self.storage = bytearray(self.sectors * self.sector_size)

    def _bounds(self, sector: int, count: int) -> tuple[int, int]:
        if sector < 0 or count <= 0 or sector + count > self.sectors:
            raise DriverError("I/O request outside device bounds")
        start = sector * self.sector_size
        return start, start + count * self.sector_size

    def read(self, sector: int, count: int = 1) -> bytes:
        start, end = self._bounds(sector, count)
        return bytes(self.storage[start:end])

    def write(self, sector: int, data: bytes) -> None:
        if len(data) % self.sector_size:
            raise DriverError("unaligned block write")
        count = len(data) // self.sector_size
        start, end = self._bounds(sector, count)
        self.storage[start:end] = data

@dataclass
class DriverManager:
    devices: dict[str, BlockDevice]

    def register(self, device: BlockDevice) -> None:
        if device.name in self.devices:
            raise DriverError("device already registered")
        self.devices[device.name] = device

    def get(self, name: str) -> BlockDevice:
        return self.devices[name]
