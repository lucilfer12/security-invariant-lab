from __future__ import annotations

from dataclasses import dataclass
import hashlib

@dataclass(frozen=True)
class BootImage:
    kernel: bytes
    version: str
    entrypoint: int

    def checksum(self) -> str:
        return hashlib.sha256(self.kernel).hexdigest()

class Bootloader:
    """Verified boot image loader for the ATLAS virtual machine."""
    MAGIC = b"ATLASBOOT1"

    def build(self, kernel: bytes, version: str, entrypoint: int = 0) -> bytes:
        if not kernel:
            raise ValueError("kernel image cannot be empty")
        if entrypoint < 0 or entrypoint >= len(kernel):
            raise ValueError("entrypoint outside kernel image")
        header = self.MAGIC + entrypoint.to_bytes(4, "big") + len(kernel).to_bytes(8, "big")
        digest = hashlib.sha256(header + kernel).digest()
        return header + digest + kernel

    def load(self, image: bytes, expected_digest: bytes | None = None) -> BootImage:
        min_size = len(self.MAGIC) + 4 + 8 + 32
        if len(image) < min_size or image[:len(self.MAGIC)] != self.MAGIC:
            raise ValueError("invalid boot image")
        pos = len(self.MAGIC)
        entrypoint = int.from_bytes(image[pos:pos + 4], "big"); pos += 4
        size = int.from_bytes(image[pos:pos + 8], "big"); pos += 8
        digest = image[pos:pos + 32]; pos += 32
        kernel = image[pos:pos + size]
        if len(kernel) != size:
            raise ValueError("truncated kernel image")
        if hashlib.sha256(image[:len(self.MAGIC) + 12] + kernel).digest() != digest:
            raise ValueError("boot image integrity check failed")
        if expected_digest is not None and digest != expected_digest:
            raise ValueError("unexpected boot image digest")
        return BootImage(kernel, "unknown", entrypoint)
