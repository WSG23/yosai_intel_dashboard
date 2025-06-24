"""
Modular database manager with protocol compliance
"""
import os
import logging
from typing import Any, Optional, Dict
import pandas as pd
from services.protocols import DatabaseProtocol
from .config_manager import DatabaseConfig

logger = logging.getLogger(__name__)

def _config_from_env() -> DatabaseConfig:
    """Create ``DatabaseConfig`` from environment variables."""
    return DatabaseConfig(
        type=os.getenv("DB_TYPE", "mock"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        name=os.getenv("DB_NAME", "yosai_db"),
        user=os.getenv("DB_USER", "yosai_user"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def validate_database_config(config: Dict[str, Any]) -> None:
    """Validate database configuration for security"""
    password = config.get('password', '')
    if password in ['', 'password', 'change-me', 'admin', 'root']:
        raise ValueError("Database password must be changed from default weak value")

    env = os.getenv('YOSAI_ENV', 'development')
    if env == 'production':
        ssl_mode = config.get('ssl_mode', 'prefer')
        if ssl_mode not in ['require', 'verify-ca', 'verify-full']:
            raise ValueError("Production database connections must use SSL (require/verify-ca/verify-full)")

    timeout = config.get('connection_timeout', 30)
    if timeout > 300:
        raise ValueError("Database connection timeout too high (max 300 seconds)")


def create_secure_connection_string(config: Dict[str, Any]) -> str:
    """Create secure database connection string"""
    validate_database_config(config)

    conn_params = {
        'host': config['host'],
        'port': config['port'],
        'database': config['database'],
        'user': config['username'],
        'password': config['password'],
        'sslmode': config.get('ssl_mode', 'prefer'),
        'connect_timeout': config.get('connection_timeout', 30),
        'application_name': 'yosai_intel_dashboard'
    }

    if config.get('ssl_mode') in ['verify-ca', 'verify-full']:
        conn_params['sslcert'] = config.get('ssl_cert')
        conn_params['sslkey'] = config.get('ssl_key')
        conn_params['sslrootcert'] = config.get('ssl_ca')

    return ';'.join(f"{k}={v}" for k, v in conn_params.items() if v is not None)

class MockDatabaseConnection:
    """Mock database connection for testing and development"""
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute mock query and return sample data"""
        # Return realistic sample data
        sample_data = {
            'event_id': ['EVT001', 'EVT002', 'EVT003', 'EVT004', 'EVT005'],
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='H'),
            'person_id': ['EMP001', 'EMP002', 'EMP001', 'EMP003', 'EMP002'],
            'door_id': ['DOOR001', 'DOOR002', 'DOOR001', 'DOOR003', 'DOOR002'],
            'access_result': ['Granted', 'Denied', 'Granted', 'Granted', 'Denied']
        }
        return pd.DataFrame(sample_data)
    
    def close(self) -> None:
        """Close connection (no-op for mock)"""
        pass

class DatabaseManager:
    """Factory for creating database connections"""
    
    @staticmethod
    def create_connection(config: DatabaseConfig) -> DatabaseProtocol:
        """Create database connection based on config"""
        if config.type == "mock":
            return MockDatabaseConnection()
        else:
            logger.warning(f"Database type '{config.type}' not implemented, using mock")
            return MockDatabaseConnection()
    
    @staticmethod
    def from_environment() -> DatabaseProtocol:
        """Create database connection from environment"""
        config = _config_from_env()
        return DatabaseManager.create_connection(config)

# Module exports
__all__ = [
    'DatabaseConfig',
    'DatabaseManager',
    'MockDatabaseConnection',
    'validate_database_config',
    'create_secure_connection_string'
]
