import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location(
    "database_manager", Path(__file__).resolve().parents[1] / "config" / "database_manager.py"
)
dbm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dbm)

DatabaseManager = dbm.DatabaseManager
DatabaseConfig = dbm.DatabaseConfig
MockConnection = dbm.MockConnection
SQLiteConnection = dbm.SQLiteConnection


def test_mock_connection():
    config = DatabaseConfig(type="mock")
    manager = DatabaseManager(config)
    conn = manager.get_connection()
    assert isinstance(conn, MockConnection)
    assert manager.health_check() is True
    manager.close()
    assert manager._connection is None


def test_sqlite_connection(tmp_path):
    db_path = tmp_path / "test.db"
    config = DatabaseConfig(type="sqlite", name=str(db_path))
    manager = DatabaseManager(config)
    conn = manager.get_connection()
    assert isinstance(conn, SQLiteConnection)
    conn.execute_command("CREATE TABLE example (id INTEGER)")
    conn.execute_command("INSERT INTO example (id) VALUES (1)")
    rows = conn.execute_query("SELECT id FROM example")
    assert rows == [{"id": 1}]
    assert manager.health_check() is True
    manager.close()
    assert manager._connection is None


def test_unknown_type_defaults_to_mock():
    config = DatabaseConfig(type="unknown")
    manager = DatabaseManager(config)
    conn = manager.get_connection()
    assert isinstance(conn, MockConnection)
    manager.close()


