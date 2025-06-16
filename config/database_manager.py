# config/database_manager.py - FIXED: Modular database management
"""
Centralized, type-safe database management for Yōsai Intel Dashboard
Handles connection pooling, configuration, and error management
"""

import os
import logging
from typing import Optional, Dict, Any, Union, TYPE_CHECKING
from contextlib import contextmanager
from dataclasses import dataclass
import pandas as pd

if TYPE_CHECKING:
    import psycopg2
    from psycopg2 import pool
    import sqlite3

# Optional imports with fallbacks
try:
    import psycopg2
    from psycopg2 import pool
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    psycopg2 = None
    pool = None

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False
    sqlite3 = None

@dataclass
class DatabaseConfig:
    """Type-safe database configuration"""
    db_type: str  # 'postgresql', 'sqlite', 'mock'
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    file_path: Optional[str] = None  # For SQLite
    pool_size: int = 5
    max_overflow: int = 10

class DatabaseConnection:
    """Abstract database connection interface"""

    def execute_query(self, query: str, params: Optional[tuple] = None) -> 'pd.DataFrame':
        raise NotImplementedError
    
    def execute_command(self, command: str, params: Optional[tuple] = None) -> None:
        raise NotImplementedError
    
    def close(self) -> None:
        raise NotImplementedError

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection with connection pooling"""
    
    def __init__(self, config: DatabaseConfig):
        if not POSTGRES_AVAILABLE:
            raise ImportError("psycopg2 not available. Install with: pip install psycopg2-binary")
        
        self.config = config
        self.connection_pool: Optional['pool.SimpleConnectionPool'] = None
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Initialize connection pool"""
        try:
            connection_string = (
                f"host={self.config.host} "
                f"port={self.config.port} "
                f"database={self.config.database} "
                f"user={self.config.username} "
                f"password={self.config.password}"
            )
            
            self.connection_pool = pool.SimpleConnectionPool(
                1, self.config.pool_size,
                connection_string
            )
            logging.info("PostgreSQL connection pool initialized")
            
        except Exception as e:
            logging.error(f"Failed to initialize PostgreSQL pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic cleanup"""
        if not self.connection_pool:
            raise RuntimeError("Connection pool not initialized")
        
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> 'pd.DataFrame':
        """Execute SELECT query and return DataFrame"""
        try:
            with self.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
        except Exception as e:
            logging.error(f"Query execution failed: {e}")
            return pd.DataFrame()
    
    def execute_command(self, command: str, params: Optional[tuple] = None) -> None:
        """Execute INSERT/UPDATE/DELETE command"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(command, params)
                conn.commit()
                cursor.close()
        except Exception as e:
            logging.error(f"Command execution failed: {e}")
            raise
    
    def close(self) -> None:
        """Close all connections in pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logging.info("PostgreSQL connection pool closed")

class SQLiteConnection(DatabaseConnection):
    """SQLite database connection for development/testing"""
    
    def __init__(self, config: DatabaseConfig):
        if not SQLITE_AVAILABLE:
            raise ImportError("sqlite3 not available")
        
        self.config = config
        self.db_path = config.file_path or "yosai_intel.db"
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """Initialize SQLite database with tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            # Create basic tables
            conn.execute('''
                CREATE TABLE IF NOT EXISTS access_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    person_id TEXT,
                    door_id TEXT,
                    access_result TEXT,
                    badge_status TEXT
                )
            ''')
            conn.commit()
            conn.close()
            logging.info(f"SQLite database initialized: {self.db_path}")
        except Exception as e:
            logging.error(f"SQLite initialization failed: {e}")
            raise
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> 'pd.DataFrame':
        """Execute query and return DataFrame"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            return df
        except Exception as e:
            logging.error(f"SQLite query failed: {e}")
            return pd.DataFrame()
    
    def execute_command(self, command: str, params: Optional[tuple] = None) -> None:
        """Execute command"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute(command, params)
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"SQLite command failed: {e}")
            raise
    
    def close(self) -> None:
        """SQLite connections close automatically"""
        pass

class MockDatabaseConnection(DatabaseConnection):
    """Mock database for testing and development"""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.sample_data = self._generate_sample_data()
        logging.info("Mock database connection initialized")
    
    def _generate_sample_data(self) -> Dict[str, 'pd.DataFrame']:
        """Generate sample data for testing"""
        from datetime import datetime, timedelta
        
        access_events = pd.DataFrame({
            'event_id': [f'EVT_{i:03d}' for i in range(100)],
            'timestamp': [datetime.now() - timedelta(hours=i) for i in range(100)],
            'person_id': [f'EMP{i%20:03d}' for i in range(100)],
            'door_id': [f'DOOR_{i%10:03d}' for i in range(100)],
            'access_result': ['Granted' if i % 4 != 0 else 'Denied' for i in range(100)],
            'badge_status': ['Valid' if i % 5 != 0 else 'Invalid' for i in range(100)]
        })
        
        return {'access_events': access_events}
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> 'pd.DataFrame':
        """Mock query execution"""
        # Simple query simulation
        if "access_events" in query.lower():
            df = self.sample_data['access_events'].copy()
            
            # Apply simple filters based on query
            if "limit" in query.lower():
                limit_match = __import__('re').search(r'limit\s+(\d+)', query.lower())
                if limit_match:
                    limit = int(limit_match.group(1))
                    df = df.head(limit)
            
            return df
        
        return pd.DataFrame()
    
    def execute_command(self, command: str, params: Optional[tuple] = None) -> None:
        """Mock command execution"""
        logging.info(f"Mock command executed: {command[:50]}...")
    
    def close(self) -> None:
        """Mock close"""
        logging.info("Mock database connection closed")

class DatabaseManager:
    """Factory for creating database connections"""
    
    @staticmethod
    def from_environment() -> DatabaseConfig:
        """Create config from environment variables"""
        db_type = os.getenv('DB_TYPE', 'mock').lower()
        
        if db_type == 'postgresql':
            return DatabaseConfig(
                db_type='postgresql',
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '5432')),
                database=os.getenv('DB_NAME', 'yosai_intel'),
                username=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                pool_size=int(os.getenv('DB_POOL_SIZE', '5'))
            )
        elif db_type == 'sqlite':
            return DatabaseConfig(
                db_type='sqlite',
                file_path=os.getenv('DB_FILE', 'yosai_intel.db')
            )
        else:
            return DatabaseConfig(db_type='mock')
    
    @staticmethod
    def create_connection(config: Optional[DatabaseConfig] = None) -> DatabaseConnection:
        """Create database connection based on configuration"""
        
        if config is None:
            config = DatabaseManager.from_environment()
        
        if config.db_type == 'postgresql':
            return PostgreSQLConnection(config)
        elif config.db_type == 'sqlite':
            return SQLiteConnection(config)
        else:
            return MockDatabaseConnection(config)
    
    @staticmethod
    def test_connection(config: Optional[DatabaseConfig] = None) -> bool:
        """Test database connection"""
        try:
            conn = DatabaseManager.create_connection(config)
            # Try a simple query
            result = conn.execute_query("SELECT 1 as test")
            conn.close()
            return not result.empty
        except Exception as e:
            logging.error(f"Database connection test failed: {e}")
            return False

# Singleton pattern for application-wide database access
_db_connection: Optional[DatabaseConnection] = None

def get_database() -> DatabaseConnection:
    """Get global database connection (singleton pattern)"""
    global _db_connection
    
    if _db_connection is None:
        config = DatabaseManager.from_environment()
        _db_connection = DatabaseManager.create_connection(config)
        logging.info(f"Global database connection established: {config.db_type}")
    
    return _db_connection

def close_database() -> None:
    """Close global database connection"""
    global _db_connection
    
    if _db_connection:
        _db_connection.close()
        _db_connection = None
        logging.info("Global database connection closed")

# Export public interface
__all__ = [
    'DatabaseConfig',
    'DatabaseConnection', 
    'DatabaseManager',
    'get_database',
    'close_database'
]