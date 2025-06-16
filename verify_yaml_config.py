#!/usr/bin/env python3
"""Verify that YAML configuration files exist and are valid."""
from pathlib import Path
from typing import List
import yaml

CONFIG_FILES: List[Path] = [
    Path("config/config.yaml"),
    Path("config/production.yaml"),
    Path("config/test.yaml"),
]


def verify_yaml_config() -> bool:
    """Return True if all configuration files exist and parse."""
    success = True
    for file_path in CONFIG_FILES:
        if not file_path.exists():
            print(f"❌ Missing {file_path}")
            success = False
            continue
        try:
            yaml.safe_load(file_path.read_text())
            print(f"✅ Valid {file_path}")
        except yaml.YAMLError as exc:
            print(f"❌ Invalid YAML in {file_path}: {exc}")
            success = False
    return success


if __name__ == "__main__":
    raise SystemExit(0 if verify_yaml_config() else 1)
