"""Simple database manager and connection helpers."""

import os
import logging
from typing import Any

from models.base import MockDatabaseConnection as _BaseMockDatabaseConnection
from .yaml_config import DatabaseConfig

logger = logging.getLogger(__name__)

class MockDatabaseConnection(_BaseMockDatabaseConnection):
    """Extension of MockDatabaseConnection with close method."""

    def close(self) -> None:
        """Close the connection (no-op for mock)."""
        pass


class DatabaseManager:
    """Factory for creating database connections."""

    @staticmethod
    def from_environment() -> DatabaseConfig:
        """Create ``DatabaseConfig`` from environment variables."""
        return DatabaseConfig(
            type=os.getenv("DB_TYPE", "mock"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "yosai_intel"),
            username=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
        )

    @staticmethod
    def create_connection(config: DatabaseConfig) -> Any:
        """Create a database connection using the provided configuration."""
        if config.type == "mock":
            return MockDatabaseConnection()
        logger.warning("Unsupported database type '%s', using mock", config.type)
        return MockDatabaseConnection()

    @staticmethod
    def test_connection(config: DatabaseConfig) -> bool:
        """Test connectivity for the given configuration."""
        try:
            conn = DatabaseManager.create_connection(config)
            conn.execute_query("SELECT 1")
            return True
        except Exception as exc:
            logger.warning("Database connection failed: %s", exc)
            return False


def get_database() -> Any:
    """Convenience helper to get a database connection from environment."""
    config = DatabaseManager.from_environment()
    return DatabaseManager.create_connection(config)


__all__ = [
    "DatabaseManager",
    "DatabaseConfig",
    "MockDatabaseConnection",
    "get_database",
]
