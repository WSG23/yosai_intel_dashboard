from typing import Any, Optional
from config.database_manager import DatabaseManager, DatabaseConfig


def create_database_connection(config: Optional[DatabaseConfig] = None) -> Any:
    """Create a database connection using DatabaseManager."""
    return DatabaseManager.create_connection(config)
