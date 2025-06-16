#!/usr/bin/env python3
"""Create and verify the YAML configuration for the project."""
from create_yaml_config_files import create_yaml_config_files
from verify_yaml_config import verify_yaml_config


def main() -> None:
    """Generate configuration files and verify them."""
    create_yaml_config_files()
    if verify_yaml_config():
        print("🎉 YAML configuration setup complete")
    else:
        print("⚠️  YAML configuration setup encountered issues")


if __name__ == "__main__":
    main()
