#!/usr/bin/env python3
"""Quick validation script for staging configuration"""

import os
from core.secret_manager import SecretManager
import yaml
import sys


def validate_staging_config():
    """Validate staging configuration"""
    print("🔧 Validating Staging Configuration")
    print("=" * 40)

    # Check if config file exists
    config_files = ["config/staging.yaml", "staging.yaml"]
    config_file = None

    for file_path in config_files:
        if os.path.exists(file_path):
            config_file = file_path
            break

    if not config_file:
        print("❌ staging.yaml not found")
        return False

    print(f"✅ Found config: {config_file}")

    # Load and validate YAML
    try:
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        print("✅ YAML syntax valid")
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False

    # Check required sections
    required_sections = ["app", "database", "security", "monitoring"]
    for section in required_sections:
        if section in config:
            print(f"✅ {section} section present")
        else:
            print(f"❌ {section} section missing")
            return False

    # Check required environment variables
    required_env_vars = ["SECRET_KEY", "DB_PASSWORD", "DB_HOST", "DB_NAME"]
    missing_vars = []

    manager = SecretManager()
    for var in required_env_vars:
        if manager.get(var, None) is None:
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing environment variables: {missing_vars}")
    else:
        print("✅ All required environment variables set")

    print(
        f"\n🎯 Staging configuration {'✅ VALID' if not missing_vars else '⚠️  NEEDS ENV VARS'}"
    )
    return len(missing_vars) == 0


if __name__ == "__main__":
    success = validate_staging_config()
    sys.exit(0 if success else 1)
