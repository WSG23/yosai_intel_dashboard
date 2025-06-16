#!/usr/bin/env python3
"""Utility to generate default YAML configuration files."""
from pathlib import Path

DEVELOPMENT_CONFIG = """\
app:
  debug: true
  host: 127.0.0.1
  port: 8050
  title: "Y\u014Dsai Intel Dashboard"
  timezone: UTC
  log_level: INFO
  enable_profiling: false

database:
  type: mock
  host: localhost
  port: 5432
  database: yosai_intel
  username: postgres
  password: ''
  pool_size: 5
  ssl_mode: prefer
  connection_timeout: 30

cache:
  type: memory
  host: localhost
  port: 6379
  database: 0
  timeout_seconds: 300
  max_memory_mb: 100
  key_prefix: 'yosai:'

security:
  secret_key: dev-key-change-in-production
  session_timeout_minutes: 60
  max_file_size_mb: 100
  allowed_file_types:
  - .csv
  - .json
  - .xlsx
  - .xls
  cors_enabled: false
  cors_origins: []

analytics:
  cache_timeout_seconds: 300
  max_records_per_query: 10000
  enable_real_time: true
  batch_size: 1000
  anomaly_detection_enabled: true
  ml_models_path: models/ml

monitoring:
  health_check_enabled: true
  metrics_enabled: true
  health_check_interval_seconds: 30
  performance_monitoring: false
  error_reporting_enabled: false
  sentry_dsn: null
"""

PRODUCTION_CONFIG = """\
app:
  debug: false
  host: 0.0.0.0
  port: 8050
  log_level: WARNING
  enable_profiling: false

database:
  type: postgresql
  host: ${DB_HOST}
  port: 5432
  database: ${DB_NAME}
  username: ${DB_USER}
  password: ${DB_PASSWORD}
  pool_size: 10
  ssl_mode: require

cache:
  type: redis
  host: ${REDIS_HOST}
  port: 6379
  timeout_seconds: 600

security:
  secret_key: ${SECRET_KEY}
  session_timeout_minutes: 30
  max_file_size_mb: 50
  cors_enabled: true
  cors_origins:
  - https://yourdomain.com

monitoring:
  health_check_enabled: true
  metrics_enabled: true
  performance_monitoring: true
  error_reporting_enabled: true
  sentry_dsn: ${SENTRY_DSN}
"""

TEST_CONFIG = """\
app:
  debug: true
  host: 127.0.0.1
  port: 8051
  log_level: DEBUG

database:
  type: mock

cache:
  type: memory
  max_memory_mb: 10

analytics:
  cache_timeout_seconds: 1
  max_records_per_query: 100

monitoring:
  health_check_enabled: false
"""


def write_config(path: Path, content: str) -> None:
    """Write a YAML config file if it does not already exist."""
    if path.exists():
        print(f"✔ {path} already exists")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"Created {path}")


def create_yaml_config_files() -> None:
    """Create all default YAML configuration files."""
    write_config(Path("config/config.yaml"), DEVELOPMENT_CONFIG)
    write_config(Path("config/production.yaml"), PRODUCTION_CONFIG)
    write_config(Path("config/test.yaml"), TEST_CONFIG)


if __name__ == "__main__":
    create_yaml_config_files()
