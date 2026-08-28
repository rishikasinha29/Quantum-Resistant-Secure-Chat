"""
Cryptographic primitives for the
Quantum-Resistant Secure Chat project.

PQC:
    CRYSTALS-Kyber / ML-KEM

Symmetric Encryption:
    AES-256-GCM

The implementation keeps secret/session keys in memory only.
"""

import base64
import hashlib
import logging
import os
from typing import Tuple

from Crypto.Cipher import AES


log = logging.getLogger("qchat.crypto")


# ============================================================
# Base64 Utilities
# ============================================================

def encode_b64(data: bytes) -> str:
    """
    Convert bytes to Base64 string.
    """
    return base64.b64encode(data).decode("ascii")


def decode_b64(data: str) -> bytes:
    """
    Convert Base64 string back to bytes.
    """
    return base64.b64decode(
        data.encode("ascii"),
        validate=True
    )


# ============================================================
# Post-Quantum KEM
# ============================================================

class PQCKEM:
    """
    Wrapper around the LibOQS KEM implementation.

    The project originally refers to CRYSTALS-Kyber.
    Modern LibOQS versions use standardized ML-KEM names.

    Supported preference:
        1. Kyber768
        2. ML-KEM-768
    """

    def __init__(self):

        try:
            import oqs

        except ImportError as exc:

            raise RuntimeError(
                "\nLibOQS Python bindings were not found.\n"
                "Please install/configure LibOQS and the oqs Python package."
            ) from exc

        self.oqs = oqs

        # Try legacy Kyber name first
        candidates = (
            "Kyber768",
            "ML-KEM-768"
        )

        try:
            available = set(
                oqs.get_enabled_kem_mechanisms()
            )

        except Exception:

            available = set()

        self.algorithm = None

        for algorithm in candidates:

            if algorithm in available:

                self.algorithm = algorithm
                break

        if self.algorithm is None:

            raise RuntimeError(
                "Neither Kyber768 nor ML-KEM-768 "
                "is available in the installed LibOQS."
            )

        self._kem = None

        self.public_key = None

    # --------------------------------------------------------
    # Generate Key Pair
    # --------------------------------------------------------

    def generate_keypair(self) -> bytes:
        """
        Generate PQC public/private key pair.

        Returns:
            public key as bytes
        """

        self._kem = self.oqs.KeyEncapsulation(
            self.algorithm
        )

        public_key = self._kem.generate_keypair()

        self.public_key = bytes(public_key)

        log.info(
            "PQC key pair generated using %s",
            self.algorithm
        )

        return self.public_key

    # --------------------------------------------------------
    # Encapsulation
    # --------------------------------------------------------

    def encapsulate(
        self,
        peer_public_key: bytes
    ) -> Tuple[bytes, bytes]:

        """
        Encapsulate a shared secret using
        the peer's public key.

        Returns:
            ciphertext
            shared secret
        """

        kem = self.oqs.KeyEncapsulation(
            self.algorithm
        )

        ciphertext, shared_secret = (
            kem.encap_secret(peer_public_key)
        )

        log.info(
            "PQC encapsulation completed"
        )

        return (
            bytes(ciphertext),
            bytes(shared_secret)
        )

    # --------------------------------------------------------
    # Decapsulation
    # --------------------------------------------------------

    def decapsulate(
        self,
        ciphertext: bytes
    ) -> bytes:

        """
        Recover the shared secret from
        KEM ciphertext.
        """

        if self._kem is None:

            raise RuntimeError(
                "Key pair has not been generated."
            )

        shared_secret = (
            self._kem.decap_secret(ciphertext)
        )

        log.info(
            "PQC decapsulation completed"
        )

        return bytes(shared_secret)

    # --------------------------------------------------------
    # Clear Secrets
    # --------------------------------------------------------

    def clear(self):

        """
        Clear references to sensitive key material.

        Native LibOQS memory management is handled by LibOQS.
        """

        self.public_key = None
        self._kem = None


# ============================================================
# AES Key Derivation
# ============================================================

def derive_aes_key(
    kem_shared_secret: bytes,
    transcript: bytes = b""
) -> bytes:

    """
    Derive a 256-bit AES key from the
    PQC shared secret.

    SHA-256 produces exactly 32 bytes.
    """

    context = (
        b"QCHAT-AES256-GCM-v1|"
        + kem_shared_secret
        + b"|"
        + transcript
    )

    return hashlib.sha256(
        context
    ).digest()


# ============================================================
# AES-256-GCM Encryption
# ============================================================

def encrypt_message(
    aes_key: bytes,
    plaintext: str
) -> dict:

    """
    Encrypt plaintext using AES-256-GCM.

    Returns:

        {
            nonce,
            ciphertext,
            tag
        }
    """

    if len(aes_key) != 32:

        raise ValueError(
            "AES-256 requires a 32-byte key."
        )

    # 96-bit nonce recommended for GCM
    nonce = os.urandom(12)

    cipher = AES.new(
        aes_key,
        AES.MODE_GCM,
        nonce=nonce
    )

    # Additional authenticated data
    cipher.update(
        b"QCHAT-v1"
    )

    ciphertext, tag = (
        cipher.encrypt_and_digest(
            plaintext.encode("utf-8")
        )
    )

    log.info(
        "Message encrypted using AES-256-GCM"
    )

    return {

        "nonce":
            encode_b64(nonce),

        "ciphertext":
            encode_b64(ciphertext),

        "tag":
            encode_b64(tag)
    }


# ============================================================
# AES-256-GCM Decryption
# ============================================================

def decrypt_message(
    aes_key: bytes,
    packet: dict
) -> str:

    """
    Verify and decrypt an AES-GCM packet.
    """

    if len(aes_key) != 32:

        raise ValueError(
            "Invalid AES-256 key."
        )

    try:

        nonce = decode_b64(
            packet["nonce"]
        )

        ciphertext = decode_b64(
            packet["ciphertext"]
        )

        tag = decode_b64(
            packet["tag"]
        )

    except (KeyError, ValueError):

        raise ValueError(
            "Malformed encrypted message."
        )

    cipher = AES.new(
        aes_key,
        AES.MODE_GCM,
        nonce=nonce
    )

    cipher.update(
        b"QCHAT-v1"
    )

    try:

        plaintext = (
            cipher.decrypt_and_verify(
                ciphertext,
                tag
            )
        )

    except ValueError:

        raise ValueError(
            "Authentication failed. "
            "Message may have been modified."
        )

    log.info(
        "Message authentication verified"
    )

    return plaintext.decode(
        "utf-8"
    )