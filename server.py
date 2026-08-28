"""
Quantum-Resistant Secure Chat
Relay Server

The relay server:

    - accepts clients
    - forwards public keys
    - forwards KEM ciphertext
    - forwards encrypted messages

The server DOES NOT:

    - generate client AES keys
    - receive private keys
    - decrypt messages
    - store plaintext messages
"""

import logging
import socket
import threading

from protocol import (
    send_json,
    recv_json
)


# ============================================================
# Configuration
# ============================================================

HOST = "0.0.0.0"
PORT = 5000

MAX_CLIENTS = 2


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "[SERVER] "
        "%(asctime)s "
        "%(levelname)s: "
        "%(message)s"
    )
)

log = logging.getLogger(
    "qchat.server"
)


# ============================================================
# Relay Server
# ============================================================

class RelayServer:

    def __init__(
        self,
        host=HOST,
        port=PORT
    ):

        self.host = host
        self.port = port

        self.clients = {}

        self.lock = threading.Lock()

    # ========================================================
    # Broadcast Packet
    # ========================================================

    def broadcast(
        self,
        sender,
        packet
    ):

        with self.lock:

            peers = [
                sock
                for sock in self.clients
                if sock is not sender
            ]

        for peer in peers:

            try:

                send_json(
                    peer,
                    packet
                )

            except OSError:

                self.remove(
                    peer
                )

    # ========================================================
    # Remove Client
    # ========================================================

    def remove(
        self,
        sock
    ):

        with self.lock:

            name = self.clients.pop(
                sock,
                None
            )

        try:

            sock.close()

        except OSError:

            pass

        if name:

            log.info(
                "%s disconnected",
                name
            )

    # ========================================================
    # Handle Client
    # ========================================================

    def handle_client(
        self,
        sock,
        address
    ):

        client_name = None

        try:

            # ------------------------------------------------
            # First packet must be HELLO
            # ------------------------------------------------

            hello = recv_json(
                sock
            )

            if hello.get("type") != "hello":

                raise ValueError(
                    "Expected hello packet."
                )

            client_name = str(
                hello.get(
                    "name",
                    "Anonymous"
                )
            )[:40]

            # ------------------------------------------------
            # Maximum room size
            # ------------------------------------------------

            with self.lock:

                if len(self.clients) >= MAX_CLIENTS:

                    send_json(
                        sock,
                        {
                            "type": "error",
                            "message":
                                "Room is full."
                        }
                    )

                    sock.close()

                    return

                self.clients[
                    sock
                ] = client_name

            log.info(
                "%s connected from %s",
                client_name,
                address
            )

            send_json(
                sock,
                {
                    "type": "status",
                    "message":
                        "Connected to relay server."
                }
            )

            # Inform existing peer
            self.broadcast(
                sock,
                {
                    "type": "peer_joined",
                    "name": client_name
                }
            )

            # ------------------------------------------------
            # Main packet loop
            # ------------------------------------------------

            while True:

                packet = recv_json(
                    sock
                )

                packet_type = (
                    packet.get("type")
                )

                # Only relay expected packets
                allowed_types = {
                    "pubkey",
                    "kem_ciphertext",
                    "message"
                }

                if packet_type in allowed_types:

                    self.broadcast(
                        sock,
                        packet
                    )

                else:

                    log.warning(
                        "Ignoring unknown packet type: %s",
                        packet_type
                    )

        except Exception as exc:

            log.warning(
                "Connection with %s ended: %s",
                client_name or address,
                exc
            )

        finally:

            self.remove(
                sock
            )

            self.broadcast(
                sock,
                {
                    "type": "peer_left"
                }
            )

    # ========================================================
    # Start Server
    # ========================================================

    def run(self):

        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        ) as listener:

            listener.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1
            )

            listener.bind(
                (
                    self.host,
                    self.port
                )
            )

            listener.listen(
                5
            )

            log.info(
                "Relay server started."
            )

            log.info(
                "Listening on %s:%d",
                self.host,
                self.port
            )

            while True:

                client_socket, address = (
                    listener.accept()
                )

                thread = threading.Thread(
                    target=self.handle_client,
                    args=(
                        client_socket,
                        address
                    ),
                    daemon=True
                )

                thread.start()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    server = RelayServer()

    try:

        server.run()

    except KeyboardInterrupt:

        print(
            "\nServer stopped."
        )