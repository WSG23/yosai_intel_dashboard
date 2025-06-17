#!/usr/bin/env python3
"""
validate_yaml_config.py - Validate YAML configuration migration
Run this after migration to ensure everything is working correctly
"""

import sys
from pathlib import Path

def validate_migration():
    """Validate that YAML configuration migration was successful"""
    print("🔍 Validating YAML Configuration Migration...")
    print("=" * 50)
    
    success = True
    
    # Check for required files
    required_files = [
        "config/config.yaml",
        "config/yaml_config.py",
        ".env.example"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            success = False
    
    # Test configuration loading
    try:
        sys.path.insert(0, '.')
        from config.yaml_config import ConfigurationManager
        
        # Test basic loading
        config_manager = ConfigurationManager()
        config_manager.load_configuration()
        
        # Test typed access
        app_config = config_manager.app_config
        db_config = config_manager.database_config
        
        print(f"✅ Configuration loading works")
        print(f"✅ App config: debug={app_config.debug}, port={app_config.port}")
        print(f"✅ Database config: type={db_config.type}, host={db_config.host}")
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        success = False
    
    # Test DI integration
    try:
        from core.service_registry import get_configured_container
        
        container = get_configured_container()
        config_manager = container.get('config_manager')
        
        print(f"✅ DI integration works")
        print(f"✅ Container has config_manager: {config_manager is not None}")
        
    except Exception as e:
        print(f"❌ DI integration failed: {e}")
        success = False
    
    print("=" * 50)
    
    if success:
        print("🎉 YAML Configuration Migration Successful!")
        print("\n📋 Next Steps:")
        print("1. Review config/config.yaml and customize for your needs")
        print("2. Copy .env.example to .env and set your environment variables")
        print("3. Test your application: python app.py")
        print("4. Create production.yaml for deployment")
    else:
        print("❌ Migration validation failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    success = validate_migration()
    sys.exit(0 if success else 1)
