"""
SQLite database module.

Stores chat history locally.

Sensitive cryptographic material such as:
    - private keys
    - KEM shared secrets
    - AES session keys

is NOT stored in the database.
"""

import sqlite3

from pathlib import Path
from datetime import datetime, timezone


class ChatDatabase:

    def __init__(
        self,
        path: str = "chat_history.db"
    ):

        self.path = Path(
            path
        )

        self.connection = sqlite3.connect(
            self.path,
            check_same_thread=False
        )

        self._create_tables()

    # ========================================================
    # Create Tables
    # ========================================================

    def _create_tables(self):

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS messages
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                timestamp TEXT NOT NULL,

                direction TEXT NOT NULL,

                peer TEXT NOT NULL,

                message TEXT NOT NULL
            )
            """
        )

        self.connection.commit()

    # ========================================================
    # Add Message
    # ========================================================

    def add_message(
        self,
        direction: str,
        peer: str,
        message: str
    ) -> None:

        timestamp = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        self.connection.execute(
            """
            INSERT INTO messages
            (
                timestamp,
                direction,
                peer,
                message
            )
            VALUES
            (?, ?, ?, ?)
            """,
            (
                timestamp,
                direction,
                peer,
                message
            )
        )

        self.connection.commit()

    # ========================================================
    # Get Messages
    # ========================================================

    def get_messages(self):

        cursor = self.connection.execute(
            """
            SELECT
                timestamp,
                direction,
                peer,
                message
            FROM messages
            ORDER BY id ASC
            """
        )

        return cursor.fetchall()

    # ========================================================
    # Close Database
    # ========================================================

    def close(self):

        if self.connection:

            self.connection.close()

            self.connection = None