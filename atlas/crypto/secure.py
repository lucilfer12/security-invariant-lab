from __future__ import annotations

import hashlib
import hmac

class CryptoUnavailable(RuntimeError):
    pass

def secure_compare(left: bytes, right: bytes) -> bool:
    return hmac.compare_digest(left, right)

def derive_key(password: bytes, salt: bytes, iterations: int = 600_000, length: int = 32) -> bytes:
    if not password or len(salt) < 16:
        raise ValueError("password must be non-empty and salt must be at least 16 bytes")
    if iterations < 100_000 or length <= 0:
        raise ValueError("unsafe KDF parameters")
    return hashlib.pbkdf2_hmac("sha256", password, salt, iterations, dklen=length)

def _backend():
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519, x25519
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise CryptoUnavailable(
            "install the optional 'cryptography' dependency for AEAD, Ed25519 and X25519"
        ) from exc
    return serialization, ed25519, x25519, AESGCM

class AEAD:
    def __init__(self, key: bytes):
        _, _, _, AESGCM = _backend()
        if len(key) not in (16, 24, 32):
            raise ValueError("AES-GCM key must be 128/192/256 bits")
        self._cipher = AESGCM(key)

    def encrypt(self, nonce: bytes, plaintext: bytes, aad: bytes | None = None) -> bytes:
        if len(nonce) != 12:
            raise ValueError("AES-GCM nonce must be 96 bits")
        return self._cipher.encrypt(nonce, plaintext, aad)

    def decrypt(self, nonce: bytes, ciphertext: bytes, aad: bytes | None = None) -> bytes:
        if len(nonce) != 12:
            raise ValueError("AES-GCM nonce must be 96 bits")
        return self._cipher.decrypt(nonce, ciphertext, aad)
class Ed25519Keypair:
    def __init__(self, private=None):
        serialization, ed25519, _, _ = _backend()
        self._private = private or ed25519.Ed25519PrivateKey.generate()
        self._serialization = serialization

    @property
    def public_key_bytes(self) -> bytes:
        return self._private.public_key().public_bytes(
            encoding=self._serialization.Encoding.Raw,
            format=self._serialization.PublicFormat.Raw,
        )

    def sign(self, message: bytes) -> bytes:
        return self._private.sign(message)

    def private_key_bytes(self) -> bytes:
        return self._private.private_bytes(
            encoding=self._serialization.Encoding.Raw,
            format=self._serialization.PrivateFormat.Raw,
            encryption_algorithm=self._serialization.NoEncryption(),
        )

class X25519:
    @staticmethod
    def generate():
        serialization, _, x25519, _ = _backend()
        private = x25519.X25519PrivateKey.generate()
        public = private.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return private, public

    @staticmethod
    def exchange(private, peer_public: bytes) -> bytes:
        _, _, x25519, _ = _backend()
        peer = x25519.X25519PublicKey.from_public_bytes(peer_public)
        return private.exchange(peer)
