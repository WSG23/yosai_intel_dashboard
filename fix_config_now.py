#!/usr/bin/env python3
"""
Immediate fix for the configuration manager issue
Save this as fix_config_now.py and run it
"""

import re
from pathlib import Path

def apply_immediate_fix():
    """Apply immediate fix to get the app running"""
    
    print("🔧 Applying immediate configuration fix...")
    
    # Fix 1: Update the load_configuration method signature
    config_file = Path("config/yaml_config.py")
    
    if config_file.exists():
        print("📝 Fixing config/yaml_config.py...")
        
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Fix method signature
        old_sig = "def load_configuration(self) -> None:"
        new_sig = "def load_configuration(self, config_path: Optional[str] = None) -> None:"
        
        if old_sig in content:
            content = content.replace(old_sig, new_sig)
            print("   ✅ Fixed method signature")
        
        # Fix method body - use effective_path
        old_path_check = "if self._config_path and Path(self._config_path).exists():"
        new_path_check = """effective_path = config_path or self._config_path
        
        # Load base configuration
        if effective_path and Path(effective_path).exists():"""
        
        if old_path_check in content:
            content = content.replace(old_path_check, new_path_check)
            print("   ✅ Fixed path handling")
        
        # Fix yaml file loading
        old_load = "self._load_yaml_file(self._config_path)"
        new_load = "self._load_yaml_file(effective_path)"
        
        if old_load in content:
            content = content.replace(old_load, new_load)
            print("   ✅ Fixed yaml file loading")
        
        # Fix logging
        old_log = 'logger.info(f"Loaded configuration from: {self._config_path}")'
        new_log = 'logger.info(f"Loaded configuration from: {effective_path}")'
        
        if old_log in content:
            content = content.replace(old_log, new_log)
            print("   ✅ Fixed logging")
        
        # Write back
        with open(config_file, 'w') as f:
            f.write(content)
        
        print("   💾 Saved changes to config/yaml_config.py")
    
    else:
        print("   ⚠️  config/yaml_config.py not found - skipping")
    
    # Fix 2: Check if we need to import Optional
    if config_file.exists():
        with open(config_file, 'r') as f:
            content = f.read()
        
        if "from typing import" in content and "Optional" not in content:
            # Add Optional to existing typing import
            content = re.sub(
                r"from typing import ([^\\n]+)",
                r"from typing import \\1, Optional",
                content
            )
            
            with open(config_file, 'w') as f:
                f.write(content)
            
            print("   ✅ Added Optional to typing imports")
    
    print("\n🚀 Configuration fix applied!")
    print("Now try: python3 app.py")

def main():
    """Main fix function"""
    print("🏯 YŌSAI INTEL DASHBOARD")
    print("⚡ IMMEDIATE CONFIGURATION FIX")
    print("=" * 50)
    
    print("Problem: ConfigurationManager.load_configuration() method signature mismatch")
    print("Solution: Update method to accept optional config_path parameter")
    print()
    
    apply_immediate_fix()
    
    print("\n" + "=" * 50)
    print("✅ READY TO TEST!")
    print("Run: python3 app.py")

if __name__ == "__main__":
    main()