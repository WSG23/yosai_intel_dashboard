#!/usr/bin/env python3
"""
Setup Missing Requirements for Yosai Dashboard
Installs missing dependencies and creates missing configuration files

Run this script to fix the issues found by the diagnostic.
"""

import os
import sys
import subprocess
from pathlib import Path


def install_missing_packages():
    """Install missing Python packages"""
    print("📦 Installing Missing Packages...")
    
    # Packages to install
    packages = [
        'flask-babel>=4.0.0',
        'python-dotenv>=1.0.0'  # For .env file support
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True, check=True)
            print(f"✅ Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    return True


def create_minimal_config():
    """Create minimal configuration files"""
    print("⚙️ Creating Configuration Files...")
    
    # Create config directory
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    print(f"✅ Created directory: {config_dir}")
    
    # Minimal config.yaml
    config_yaml = """
# Minimal Yosai Configuration
app:
  title: "Yosai Intelligence Dashboard"
  debug: true
  host: "127.0.0.1"
  port: 8050
  log_level: "INFO"

database:
  host: "localhost"
  port: 5432
  name: "yosai_db"
  user: "yosai_user"
  password: "dev_password"

security:
  secret_key: "dev-secret-key-change-in-production"
  session_timeout: 3600

analytics:
  enabled: true
  batch_size: 100

monitoring:
  health_check_interval: 30
  metrics_enabled: true

cache:
  type: "memory"
  ttl: 300
"""
    
    config_file = config_dir / 'config.yaml'
    with open(config_file, 'w') as f:
        f.write(config_yaml.strip())
    print(f"✅ Created: {config_file}")
    
    # Create production config (copy of main config)
    prod_config = config_dir / 'production.yaml'
    with open(prod_config, 'w') as f:
        f.write(config_yaml.replace('debug: true', 'debug: false').strip())
    print(f"✅ Created: {prod_config}")
    
    # Create test config
    test_config = config_dir / 'test.yaml'
    with open(test_config, 'w') as f:
        f.write(config_yaml.replace('port: 8050', 'port: 8051').strip())
    print(f"✅ Created: {test_config}")
    
    return True


def create_env_file():
    """Create .env file with necessary environment variables"""
    print("🔧 Creating Environment File...")
    
    env_content = """# Yosai Dashboard Environment Variables

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-change-in-production

# Yosai Configuration
YOSAI_ENV=development
YOSAI_CONFIG_FILE=config/config.yaml

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=yosai_db
DB_USER=yosai_user
DB_PASSWORD=dev_password

# Auth0 Configuration (Development)
AUTH0_CLIENT_ID=dev-client-id
AUTH0_CLIENT_SECRET=dev-client-secret
AUTH0_DOMAIN=dev-domain.auth0.com

# Security
WTF_CSRF_ENABLED=False

# Additional
DEBUG=1
"""
    
    env_file = Path('.env')
    
    # Don't overwrite existing .env file
    if env_file.exists():
        print(f"⚠️ .env file already exists, creating .env.example instead")
        env_file = Path('.env.example')
    
    with open(env_file, 'w') as f:
        f.write(env_content.strip())
    print(f"✅ Created: {env_file}")
    
    return True


def test_imports():
    """Test that imports work after setup"""
    print("🧪 Testing Imports...")
    
    try:
        import flask_babel
        print("✅ flask-babel import successful")
    except ImportError as e:
        print(f"❌ flask-babel import failed: {e}")
        return False
    
    try:
        from config.yaml_config import ConfigurationManager
        print("✅ ConfigurationManager import successful")
    except ImportError as e:
        print(f"❌ ConfigurationManager import failed: {e}")
        return False
    
    try:
        from core.app_factory import create_application
        print("✅ create_application import successful")
    except ImportError as e:
        print(f"❌ create_application import failed: {e}")
        return False
    
    return True


def main():
    """Main setup function"""
    print("🚀 Yosai Dashboard Setup")
    print("=" * 40)
    print("Fixing issues found by diagnostic...\n")
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Install missing packages
    if install_missing_packages():
        success_count += 1
        print()
    
    # Step 2: Create config files
    if create_minimal_config():
        success_count += 1
        print()
    
    # Step 3: Create .env file
    if create_env_file():
        success_count += 1
        print()
    
    # Step 4: Test imports
    if test_imports():
        success_count += 1
        print()
    
    # Report results
    print("📊 Setup Results")
    print("-" * 20)
    print(f"Completed: {success_count}/{total_steps} steps")
    
    if success_count == total_steps:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Next Steps:")
        print("1. Run diagnostic again: python3 app_diagnostic.py")
        print("2. Start protected app: python3 app_launcher.py --mode protected")
        print("3. If you still have AUTH0 issues, check your actual AUTH0 credentials")
        return 0
    else:
        print("⚠️ Some setup steps failed. Check the errors above.")
        print("\n🔧 Manual Steps:")
        print("1. Install flask-babel: pip install flask-babel")
        print("2. Create config/config.yaml with your settings")
        print("3. Set AUTH0_CLIENT_ID environment variable")
        return 1


if __name__ == "__main__":
    sys.exit(main())
    