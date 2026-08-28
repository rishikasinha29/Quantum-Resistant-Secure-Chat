"""
Length-prefixed JSON communication protocol.

Every packet has:

    4-byte packet length
    +
    JSON payload
"""

import json
import struct


# Maximum packet size: 2 MB
MAX_PACKET = 2 * 1024 * 1024


# ============================================================
# Send JSON Packet
# ============================================================

def send_json(sock, obj: dict) -> None:

    """
    Serialize dictionary to JSON and send it
    with a 4-byte network-order length prefix.
    """

    raw = json.dumps(
        obj,
        separators=(",", ":")
    ).encode("utf-8")

    if len(raw) > MAX_PACKET:

        raise ValueError(
            "Packet exceeds maximum allowed size."
        )

    header = struct.pack(
        "!I",
        len(raw)
    )

    sock.sendall(
        header + raw
    )


# ============================================================
# Receive Exact Number of Bytes
# ============================================================

def recv_exact(
    sock,
    n: int
) -> bytes:

    """
    Receive exactly n bytes.
    """

    chunks = []

    remaining = n

    while remaining > 0:

        chunk = sock.recv(
            remaining
        )

        if not chunk:

            raise ConnectionError(
                "Peer closed the connection."
            )

        chunks.append(
            chunk
        )

        remaining -= len(chunk)

    return b"".join(
        chunks
    )


# ============================================================
# Receive JSON Packet
# ============================================================

def recv_json(sock) -> dict:

    """
    Receive a length-prefixed JSON packet.
    """

    header = recv_exact(
        sock,
        4
    )

    length = struct.unpack(
        "!I",
        header
    )[0]

    if length <= 0:

        raise ValueError(
            "Invalid packet length."
        )

    if length > MAX_PACKET:

        raise ValueError(
            "Packet is too large."
        )

    raw = recv_exact(
        sock,
        length
    )

    try:

        packet = json.loads(
            raw.decode("utf-8")
        )

    except (UnicodeDecodeError, json.JSONDecodeError):

        raise ValueError(
            "Invalid JSON packet."
        )

    if not isinstance(packet, dict):

        raise ValueError(
            "Packet must be a JSON object."
        )

    return packet