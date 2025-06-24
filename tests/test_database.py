"""Database layer tests"""
import pandas as pd
import pytest
from database.connection import SQLiteConnection, MockConnection
from core.exceptions import DatabaseError

class TestDatabaseConnections:
    def test_mock_connection_basic_operations(self):
        conn = MockConnection()
        df = conn.execute_query("SELECT * FROM access_events LIMIT 5")
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 5
        result = conn.execute_command("INSERT INTO access_events VALUES (1)")
        assert result == 1
        assert conn.health_check() is True

    def test_sqlite_connection_initialization(self, tmp_path):
        db_path = tmp_path / "test.db"
        conn = SQLiteConnection(str(db_path))
        assert db_path.exists()
        assert conn.health_check() is True
        df = conn.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        assert 'access_events' in df['name'].values

    def test_sqlite_connection_query_error(self, tmp_path):
        db_path = tmp_path / "test.db"
        conn = SQLiteConnection(str(db_path))
        with pytest.raises(DatabaseError):
            conn.execute_query("SELECT * FROM nonexistent_table")
