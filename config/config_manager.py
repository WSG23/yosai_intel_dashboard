"""Simplified configuration loader used for tests."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os
import yaml

from core.exceptions import ConfigurationError

@dataclass
class DatabaseConfig:
    type: str = "sqlite"
    name: str = "app.db"
    host: str = "localhost"

@dataclass
class AppConfig:
    debug: bool = False
    port: int = 8050
    environment: str = "development"

@dataclass
class Config:
    database: DatabaseConfig
    app: AppConfig

class ConfigManager:
    """Load configuration from YAML with env overrides."""

    def __init__(self, config_dir: Optional[str] = None) -> None:
        self.config_dir = Path(config_dir) if config_dir else None

    def load_config(self) -> Config:
        config = Config(database=DatabaseConfig(), app=AppConfig())

        # Load YAML if directory provided
        if self.config_dir:
            path = self.config_dir / "config.yaml"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                app_data = data.get("app", {})
                db_data = data.get("database", {})
                for key, value in app_data.items():
                    setattr(config.app, key, value)
                for key, value in db_data.items():
                    setattr(config.database, key, value)

        # Environment variable overrides
        if "DEBUG" in os.environ:
            config.app.debug = os.environ["DEBUG"].lower() == "true"
        if "PORT" in os.environ:
            config.app.port = int(os.environ["PORT"])
        if "DB_TYPE" in os.environ:
            config.database.type = os.environ["DB_TYPE"]
        env = os.getenv("YOSAI_ENV", "development")
        config.app.environment = env
        if env == "production":
            raise ConfigurationError("Production requires secure settings")

        return config
