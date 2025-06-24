"""Simplified database connection management.

This module replaces the previous over engineered abstraction with a small set
of utilities for obtaining database connections.  SQLite and a mock database
are supported out of the box.  PostgreSQL can be implemented later if needed.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional, Protocol

import pandas as pd


from core.exceptions import DatabaseError


@dataclass
class DatabaseConfig:
    """Minimal database configuration."""

    type: str = "mock"
    host: str = "localhost"
    port: int = 5432
    name: str = "yosai_db"
    user: str = "yosai_user"
    password: str = ""

    # Backwards compatible alias used in some tests
    @property
    def db_type(self) -> str:  # pragma: no cover - simple alias
        return self.type


class DatabaseConnection(Protocol):
    """Protocol all database connections must follow."""

    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        ...

    def execute_command(self, command: str, params: Optional[tuple] = None) -> int:
        ...

    def health_check(self) -> bool:
        ...


class SQLiteConnection:
    """Lightweight SQLite connection wrapper."""

    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._ensure_database_exists()

    def _ensure_database_exists(self) -> None:
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS access_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        user_id TEXT,
                        event_type TEXT,
                        location TEXT,
                        status TEXT,
                        details TEXT
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as exc:  # pragma: no cover - initialization failure
            raise DatabaseError(f"Failed to initialize database: {exc}") from exc

    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        try:
            with sqlite3.connect(self.database_path) as conn:
                return pd.read_sql_query(query, conn, params=params)
        except (sqlite3.Error, pd.errors.DatabaseError) as exc:
            raise DatabaseError(f"Query failed: {exc}") from exc

    def execute_command(self, command: str, params: Optional[tuple] = None) -> int:
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.execute(command, params or ())
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as exc:
            raise DatabaseError(f"Command failed: {exc}") from exc

    def health_check(self) -> bool:
        try:
            with sqlite3.connect(self.database_path) as conn:
                conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False


class MockConnection:
    """In-memory mock connection used for unit tests."""

    def __init__(self) -> None:
        self._data = self._generate_mock_data()

    def _generate_mock_data(self) -> pd.DataFrame:
        import datetime
        import random

        data = []
        base_time = datetime.datetime.now()

        for i in range(100):
            data.append(
                {
                    "id": i + 1,
                    "timestamp": base_time - datetime.timedelta(hours=random.randint(0, 168)),
                    "user_id": f"user_{random.randint(1, 20):03d}",
                    "event_type": random.choice(["entry", "exit", "access_denied"]),
                    "location": random.choice(["main_entrance", "parking_gate", "office_door"]),
                    "status": random.choice(["success", "failed", "pending"]),
                    "details": f"Event details {i + 1}",
                }
            )

        return pd.DataFrame(data)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
        if "LIMIT" in query.upper():
            limit = int(query.upper().split("LIMIT")[-1].strip())
            return self._data.head(limit)
        return self._data

    def execute_command(self, command: str, params: Optional[tuple] = None) -> int:
        return 1

    def health_check(self) -> bool:
        return True



class DatabaseManager:
    """Create and manage database connections."""

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self._connection: Optional[DatabaseConnection] = None

    def get_connection(self) -> DatabaseConnection:
        if self._connection is None:
            self._connection = self._create_connection()
        return self._connection

    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------
    @staticmethod
    def create_connection(config: DatabaseConfig) -> DatabaseConnection:
        """Create a connection without instantiating ``DatabaseManager``."""

        return DatabaseManager(config).get_connection()

    @staticmethod
    def from_environment() -> DatabaseConfig:
        """Load configuration from environment variables."""

        return DatabaseConfig(
            type=os.getenv("DB_TYPE", "mock"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "yosai_db"),
            user=os.getenv("DB_USER", "yosai_user"),
            password=os.getenv("DB_PASSWORD", ""),
        )

    # ------------------------------------------------------------------

    def _create_connection(self) -> DatabaseConnection:
        cfg_type = getattr(self.config, "type", getattr(self.config, "db_type", "mock"))
        if cfg_type == "sqlite":
            return SQLiteConnection(self.config.name)
        if cfg_type == "mock":
            return MockConnection()
        if cfg_type == "postgresql":  # pragma: no cover - future work
            raise DatabaseError("PostgreSQL support not implemented yet")
        raise DatabaseError(f"Unsupported database type: {cfg_type}")

    @contextmanager
    def transaction(self):
        connection = self.get_connection()
        try:
            yield connection
        except Exception as exc:  # pragma: no cover - basic pass-through
            raise DatabaseError(f"Transaction failed: {exc}") from exc


def get_database() -> DatabaseConnection:
    """Convenience helper to obtain a connection from environment settings."""

    config = DatabaseManager.from_environment()
    return DatabaseManager.create_connection(config)


def create_database_manager(config: DatabaseConfig) -> DatabaseManager:
    """Factory function used by dependency injection systems."""

    return DatabaseManager(config)


__all__ = [
    "DatabaseConfig",
    "DatabaseConnection",
    "SQLiteConnection",
    "MockConnection",
    "DatabaseManager",
    "create_database_manager",
    "get_database",
]

