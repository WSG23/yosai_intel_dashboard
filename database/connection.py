"""Database connection utilities for tests."""
from __future__ import annotations

import sqlite3
from pathlib import Path
import pandas as pd

from core.exceptions import DatabaseError

class MockConnection:
    """In-memory mock connection returning sample data."""

    def execute_query(self, query: str):
        data = {
            'id': [1, 2, 3, 4, 5],
            'value': [10, 20, 30, 40, 50],
        }
        return pd.DataFrame(data)

    def execute_command(self, command: str) -> int:
        return 1

    def health_check(self) -> bool:
        return True

class SQLiteConnection:
    """Simple SQLite connection wrapper."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        initialize = not self.path.exists()
        self.conn = sqlite3.connect(str(self.path))
        if initialize:
            self._initialize_db()

    def _initialize_db(self) -> None:
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS access_events (id INTEGER PRIMARY KEY, value TEXT)"
        )
        self.conn.commit()

    def execute_query(self, query: str):
        try:
            return pd.read_sql_query(query, self.conn)
        except Exception as e:
            raise DatabaseError(str(e)) from e

    def execute_command(self, command: str) -> int:
        try:
            cur = self.conn.execute(command)
            self.conn.commit()
            return cur.rowcount
        except Exception as e:
            raise DatabaseError(str(e)) from e

    def health_check(self) -> bool:
        try:
            self.conn.execute("SELECT 1")
            return True
        except Exception:
            return False
