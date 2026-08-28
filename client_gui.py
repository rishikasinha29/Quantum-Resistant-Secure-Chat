"""
Quantum-Resistant Secure Chat
PyQt5 Client

Features:

    - PyQt5 GUI
    - CRYSTALS-Kyber / ML-KEM
    - AES-256-GCM
    - TCP networking
    - SQLite logging
    - Terminal debug logging
"""

import argparse
import base64
import logging
import socket
import sys
import threading


from PyQt5.QtCore import (
    QObject,
    pyqtSignal
)

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget
)


from crypto import (
    PQCKEM,
    derive_aes_key,
    encrypt_message,
    decrypt_message
)


from database import (
    ChatDatabase
)


from protocol import (
    send_json,
    recv_json
)


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "[CLIENT] "
        "%(asctime)s "
        "%(levelname)s: "
        "%(message)s"
    )
)

log = logging.getLogger(
    "qchat.client"
)


# ============================================================
# GUI Events
# ============================================================

class Events(QObject):

    status = pyqtSignal(str)

    incoming = pyqtSignal(
        str,
        str
    )

    error = pyqtSignal(str)

    connected = pyqtSignal()

    secure_ready = pyqtSignal()


# ============================================================
# Secure Chat Client
# ============================================================

class SecureChatClient:

    def __init__(
        self,
        name,
        events,
        host,
        port
    ):

        self.name = name

        self.events = events

        self.host = host

        self.port = port

        self.sock = None

        self.running = False

        self.kem = None

        self.aes_key = None

        self.peer_name = "Peer"

        # Local database
        self.db = ChatDatabase(
            f"{name}_chat.db"
        )

    # ========================================================
    # Connect
    # ========================================================

    def connect(self):

        log.info(
            "Connecting to %s:%d",
            self.host,
            self.port
        )

        self.sock = socket.create_connection(
            (
                self.host,
                self.port
            ),
            timeout=10
        )

        self.sock.settimeout(
            None
        )

        self.running = True

        # ----------------------------------------------------
        # Send HELLO
        # ----------------------------------------------------

        send_json(
            self.sock,
            {
                "type": "hello",
                "name": self.name
            }
        )

        log.info(
            "HELLO packet sent."
        )

        # ----------------------------------------------------
        # Generate PQC keys
        # ----------------------------------------------------

        self.kem = PQCKEM()

        public_key = (
            self.kem.generate_keypair()
        )

        log.info(
            "PQC algorithm: %s",
            self.kem.algorithm
        )

        # ----------------------------------------------------
        # Send public key
        # ----------------------------------------------------

        send_json(
            self.sock,
            {
                "type": "pubkey",

                "name":
                    self.name,

                "public_key":
                    base64.b64encode(
                        public_key
                    ).decode(
                        "ascii"
                    )
            }
        )

        log.info(
            "PQC public key transmitted."
        )

        # ----------------------------------------------------
        # Start receiver thread
        # ----------------------------------------------------

        threading.Thread(
            target=self.receive_loop,
            daemon=True
        ).start()

        self.events.connected.emit()

    # ========================================================
    # Receive Loop
    # ========================================================

    def receive_loop(self):

        try:

            while self.running:

                packet = recv_json(
                    self.sock
                )

                packet_type = (
                    packet.get("type")
                )

                # --------------------------------------------
                # Status
                # --------------------------------------------

                if packet_type == "status":

                    self.events.status.emit(
                        packet.get(
                            "message",
                            "Connected."
                        )
                    )

                # --------------------------------------------
                # Peer Joined
                # --------------------------------------------

                elif packet_type == "peer_joined":

                    self.peer_name = (
                        packet.get(
                            "name",
                            "Peer"
                        )
                    )

                    self.events.status.emit(
                        f"{self.peer_name} joined."
                    )

                # --------------------------------------------
                # Peer Left
                # --------------------------------------------

                elif packet_type == "peer_left":

                    self.events.status.emit(
                        "Peer disconnected."
                    )

                    self.clear_session()

                # --------------------------------------------
                # Error
                # --------------------------------------------

                elif packet_type == "error":

                    self.events.error.emit(
                        packet.get(
                            "message",
                            "Server error."
                        )
                    )

                # --------------------------------------------
                # Public Key
                # --------------------------------------------

                elif packet_type == "pubkey":

                    self.handle_public_key(
                        packet
                    )

                # --------------------------------------------
                # KEM Ciphertext
                # --------------------------------------------

                elif packet_type == "kem_ciphertext":

                    self.handle_kem_ciphertext(
                        packet
                    )

                # --------------------------------------------
                # Encrypted Message
                # --------------------------------------------

                elif packet_type == "message":

                    self.handle_message(
                        packet
                    )

        except Exception as exc:

            if self.running:

                log.exception(
                    "Receive loop terminated."
                )

                self.events.error.emit(
                    f"Connection closed: {exc}"
                )

        finally:

            self.running = False

    # ========================================================
    # Handle Public Key
    # ========================================================

    def handle_public_key(
        self,
        packet
    ):

        try:

            self.peer_name = packet.get(
                "name",
                "Peer"
            )

            peer_public_key = (
                base64.b64decode(
                    packet[
                        "public_key"
                    ]
                )
            )

            log.info(
                "Received %s's PQC public key.",
                self.peer_name
            )

            # ------------------------------------------------
            # Encapsulate
            # ------------------------------------------------

            ciphertext, shared_secret = (
                self.kem.encapsulate(
                    peer_public_key
                )
            )

            # ------------------------------------------------
            # Derive AES key
            # ------------------------------------------------

            self.aes_key = (
                derive_aes_key(
                    shared_secret
                )
            )

            log.info(
                "Shared secret established."
            )

            log.info(
                "AES-256 session key derived."
            )

            # ------------------------------------------------
            # Send KEM ciphertext
            # ------------------------------------------------

            send_json(
                self.sock,
                {
                    "type":
                        "kem_ciphertext",

                    "ciphertext":
                        base64.b64encode(
                            ciphertext
                        ).decode(
                            "ascii"
                        )
                }
            )

            log.info(
                "KEM ciphertext sent."
            )

            self.events.status.emit(
                "Secure session established."
            )

            self.events.secure_ready.emit()

        except Exception as exc:

            log.exception(
                "PQC public-key processing failed."
            )

            self.events.error.emit(
                f"PQC handshake failed: {exc}"
            )

    # ========================================================
    # Handle KEM Ciphertext
    # ========================================================

    def handle_kem_ciphertext(
        self,
        packet
    ):

        try:

            ciphertext = (
                base64.b64decode(
                    packet[
                        "ciphertext"
                    ]
                )
            )

            # ------------------------------------------------
            # Decapsulate
            # ------------------------------------------------

            shared_secret = (
                self.kem.decapsulate(
                    ciphertext
                )
            )

            # ------------------------------------------------
            # Derive AES key
            # ------------------------------------------------

            self.aes_key = (
                derive_aes_key(
                    shared_secret
                )
            )

            log.info(
                "KEM ciphertext decapsulated."
            )

            log.info(
                "AES-256-GCM session established."
            )

            self.events.status.emit(
                "Secure session established."
            )

            self.events.secure_ready.emit()

        except Exception as exc:

            log.exception(
                "KEM decapsulation failed."
            )

            self.events.error.emit(
                f"Secure handshake failed: {exc}"
            )

    # ========================================================
    # Handle Incoming Message
    # ========================================================

    def handle_message(
        self,
        packet
    ):

        if self.aes_key is None:

            self.events.error.emit(
                "Encrypted message received "
                "before secure session."
            )

            return

        try:

            plaintext = decrypt_message(
                self.aes_key,
                packet["payload"]
            )

            log.info(
                "Encrypted message received."
            )

            # Store plaintext locally
            self.db.add_message(
                "received",
                self.peer_name,
                plaintext
            )

            self.events.incoming.emit(
                self.peer_name,
                plaintext
            )

        except Exception:

            log.exception(
                "Message authentication failed."
            )

            self.events.error.emit(
                "Message rejected: "
                "authentication failed."
            )

    # ========================================================
    # Send Message
    # ========================================================

    def send_message(
        self,
        text
    ):

        text = text.strip()

        if not text:

            return

        if self.aes_key is None:

            self.events.error.emit(
                "Secure session is not ready."
            )

            return

        # ----------------------------------------------------
        # AES-256-GCM encryption
        # ----------------------------------------------------

        encrypted = encrypt_message(
            self.aes_key,
            text
        )

        packet = {

            "type":
                "message",

            "payload":
                encrypted
        }

        send_json(
            self.sock,
            packet
        )

        log.info(
            "Encrypted message transmitted."
        )

        # ----------------------------------------------------
        # Store locally
        # ----------------------------------------------------

        self.db.add_message(
            "sent",
            self.peer_name,
            text
        )

        # Display local message
        self.events.incoming.emit(
            "You",
            text
        )

    # ========================================================
    # Clear Session
    # ========================================================

    def clear_session(self):

        self.aes_key = None

        if self.kem:

            self.kem.clear()

            self.kem = None

        log.info(
            "Session cryptographic material cleared."
        )

    # ========================================================
    # Close Client
    # ========================================================

    def close(self):

        self.running = False

        self.clear_session()

        if self.sock:

            try:

                self.sock.shutdown(
                    socket.SHUT_RDWR
                )

            except Exception:

                pass

            try:

                self.sock.close()

            except Exception:

                pass

        self.db.close()


# ============================================================
# Main GUI Window
# ============================================================

class MainWindow(QMainWindow):

    def __init__(
        self,
        args
    ):

        super().__init__()

        self.setWindowTitle(
            "Quantum-Resistant Secure Chat"
        )

        self.resize(
            800,
            600
        )

        # ----------------------------------------------------
        # Events
        # ----------------------------------------------------

        self.events = Events()

        # ----------------------------------------------------
        # Client
        # ----------------------------------------------------

        self.client = SecureChatClient(
            args.name,
            self.events,
            args.host,
            args.port
        )

        # ----------------------------------------------------
        # User label
        # ----------------------------------------------------

        self.user_label = QLabel(
            f"User: {args.name}"
        )

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status = QLabel(
            "Connecting..."
        )

        # ----------------------------------------------------
        # Chat display
        # ----------------------------------------------------

        self.chat = QTextEdit()

        self.chat.setReadOnly(
            True
        )

        # ----------------------------------------------------
        # Message input
        # ----------------------------------------------------

        self.input = QLineEdit()

        self.input.setPlaceholderText(
            "Type your secure message..."
        )

        # ----------------------------------------------------
        # Send button
        # ----------------------------------------------------

        self.send_button = QPushButton(
            "Send"
        )

        self.send_button.setEnabled(
            False
        )

        # ----------------------------------------------------
        # Input row
        # ----------------------------------------------------

        input_layout = QHBoxLayout()

        input_layout.addWidget(
            self.input
        )

        input_layout.addWidget(
            self.send_button
        )

        # ----------------------------------------------------
        # Main layout
        # ----------------------------------------------------

        layout = QVBoxLayout()

        layout.addWidget(
            self.user_label
        )

        layout.addWidget(
            self.status
        )

        layout.addWidget(
            self.chat
        )

        layout.addLayout(
            input_layout
        )

        root = QWidget()

        root.setLayout(
            layout
        )

        self.setCentralWidget(
            root
        )

        # ----------------------------------------------------
        # Signals
        # ----------------------------------------------------

        self.send_button.clicked.connect(
            self.send_message
        )

        self.input.returnPressed.connect(
            self.send_message
        )

        self.events.status.connect(
            self.set_status
        )

        self.events.incoming.connect(
            self.add_message
        )

        self.events.error.connect(
            self.show_error
        )

        self.events.connected.connect(
            self.connected
        )

        self.events.secure_ready.connect(
            self.secure_ready
        )

        # ----------------------------------------------------
        # Connect in background
        # ----------------------------------------------------

        threading.Thread(
            target=self.connect_client,
            daemon=True
        ).start()

    # ========================================================
    # Connect Client
    # ========================================================

    def connect_client(self):

        try:

            self.client.connect()

        except Exception as exc:

            log.exception(
                "Client connection failed."
            )

            self.events.error.emit(
                str(exc)
            )

    # ========================================================
    # Connected
    # ========================================================

    def connected(self):

        self.set_status(
            "Connected. Performing PQC handshake..."
        )

    # ========================================================
    # Secure Session Ready
    # ========================================================

    def secure_ready(self):

        self.status.setText(
            "🔐 Secure Session Ready "
            "(PQC + AES-256-GCM)"
        )

        self.send_button.setEnabled(
            True
        )

    # ========================================================
    # Status
    # ========================================================

    def set_status(
        self,
        text
    ):

        self.status.setText(
            text
        )

        self.send_button.setEnabled(
            self.client.aes_key is not None
        )

    # ========================================================
    # Display Message
    # ========================================================

    def add_message(
        self,
        sender,
        text
    ):

        self.chat.append(
            f"<b>{sender}:</b> {text}"
        )

        self.send_button.setEnabled(
            self.client.aes_key is not None
        )

    # ========================================================
    # Send Message
    # ========================================================

    def send_message(self):

        text = self.input.text()

        if not text.strip():

            return

        try:

            self.client.send_message(
                text
            )

            self.input.clear()

        except Exception as exc:

            self.show_error(
                str(exc)
            )

    # ========================================================
    # Show Error
    # ========================================================

    def show_error(
        self,
        text
    ):

        self.status.setText(
            "Error: " + text
        )

        log.error(
            text
        )

        QMessageBox.warning(
            self,
            "Secure Chat",
            text
        )

    # ========================================================
    # Close Event
    # ========================================================

    def closeEvent(
        self,
        event
    ):

        self.client.close()

        event.accept()


# ============================================================
# Main
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Quantum-Resistant Secure Chat Client"
        )
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Username"
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Relay server IP"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Relay server port"
    )

    args = parser.parse_args()

    app = QApplication(
        sys.argv
    )

    window = MainWindow(
        args
    )

    window.show()

    sys.exit(
        app.exec_()
    )


if __name__ == "__main__":

    main()