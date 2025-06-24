"""Configuration system tests"""
import os
from pathlib import Path
import pytest
from config.config_manager import ConfigManager, Config
from core.exceptions import ConfigurationError

class TestConfigManager:
    def test_default_config_creation(self):
        manager = ConfigManager()
        cfg = manager.load_config()
        assert isinstance(cfg, Config)
        assert cfg.app.debug is False
        assert cfg.database.type == "sqlite"

    def test_environment_variable_override(self, monkeypatch):
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("DB_TYPE", "postgresql")
        monkeypatch.setenv("PORT", "8080")
        manager = ConfigManager()
        cfg = manager.load_config()
        assert cfg.app.debug is True
        assert cfg.database.type == "postgresql"
        assert cfg.app.port == 8080

    def test_yaml_config_loading(self, tmp_path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        yaml_content = """
        app:
          debug: true
          port: 9000
        database:
          type: postgresql
          host: test-host
        """
        (config_dir / "config.yaml").write_text(yaml_content)
        manager = ConfigManager(str(config_dir))
        cfg = manager.load_config()
        assert cfg.app.debug is True
        assert cfg.app.port == 9000
        assert cfg.database.type == "postgresql"
        assert cfg.database.host == "test-host"

    def test_production_validation(self, monkeypatch):
        monkeypatch.setenv("YOSAI_ENV", "production")
        manager = ConfigManager()
        with pytest.raises(ConfigurationError, match="Production requires"):
            manager.load_config()
