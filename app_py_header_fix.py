#!/usr/bin/env python3
"""
Fix app.py to load .env at the very beginning
"""

from pathlib import Path


def fix_app_py():
    """Add .env loading to the top of app.py"""
    app_file = Path("app.py")
    
    if not app_file.exists():
        print("❌ app.py not found")
        return False
    
    # Read current content
    with open(app_file, 'r') as f:
        content = f.read()
    
    # Check if already fixed
    if "load_dotenv" in content:
        print("✅ app.py already has .env loading")
        return True
    
    # Backup original
    backup_file = Path("app.py.backup")
    with open(backup_file, 'w') as f:
        f.write(content)
    print(f"✅ Backed up app.py to {backup_file}")
    
    # Add .env loading at the top
    env_loading_code = '''#!/usr/bin/env python3
"""
CRITICAL: Load .env file FIRST before any other imports
"""
import os
from pathlib import Path

# Force load .env file before importing anything else
try:
    from dotenv import load_dotenv
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file, override=True)
        print("✅ Loaded .env file")
    else:
        print("⚠️  .env file not found")
except ImportError:
    print("⚠️  python-dotenv not installed")

# Ensure critical variables are set
required_vars = {
    "DB_HOST": "localhost",
    "SECRET_KEY": "dev-secret-change-in-production-12345",
    "AUTH0_CLIENT_ID": "your-client-id",
    "AUTH0_CLIENT_SECRET": "your-client-secret", 
    "AUTH0_DOMAIN": "your-domain.auth0.com",
    "AUTH0_AUDIENCE": "your-api-audience",
    "YOSAI_ENV": "development"
}

for var, default in required_vars.items():
    if not os.getenv(var):
        os.environ[var] = default

'''
    
    # Find where to insert (after shebang and docstring)
    lines = content.split('\n')
    insert_index = 0
    
    # Skip shebang
    if lines[0].startswith('#!'):
        insert_index = 1
    
    # Skip module docstring
    in_docstring = False
    for i, line in enumerate(lines[insert_index:], insert_index):
        if '"""' in line or "'''" in line:
            if not in_docstring:
                in_docstring = True
            else:
                insert_index = i + 1
                break
        elif not in_docstring and line.strip() and not line.startswith('#'):
            insert_index = i
            break
    
    # Insert the .env loading code
    lines.insert(insert_index, env_loading_code)
    
    # Write fixed content
    with open(app_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Fixed app.py - added .env loading at the top")
    return True


def main():
    print("🔧 Fixing app.py to Load .env First")
    print("=" * 35)
    
    if fix_app_py():
        print("\n🎉 app.py fixed successfully!")
        print("\n🚀 Now run: python3 app.py")
    else:
        print("\n❌ Failed to fix app.py")
        print("🚀 Use the launcher instead: python3 launch_app.py")


if __name__ == "__main__":
    main()