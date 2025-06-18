#!/usr/bin/env python3
"""
Fix Dash API - Replace run_server with run
"""

import re
from pathlib import Path


def fix_dash_api_calls():
    """Fix all occurrences of app.run_server to app.run"""
    files_to_fix = [
        "debug_json_error.py",
        "minimal_working_app.py", 
        "launch_json_safe.py",
        "launch_app.py",
        "simple_app.py",
        "app.py"
    ]
    
    fixes_applied = []
    
    for file_name in files_to_fix:
        file_path = Path(file_name)
        if not file_path.exists():
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Replace run_server with run
            if 'run_server(' in content:
                updated_content = content.replace('.run_server(', '.run(')
                
                with open(file_path, 'w') as f:
                    f.write(updated_content)
                
                print(f"✅ Fixed {file_name}")
                fixes_applied.append(file_name)
            
        except Exception as e:
            print(f"❌ Error fixing {file_name}: {e}")
    
    return fixes_applied


def test_your_app():
    """Test your app with the fixed debugger"""
    # Load environment first
    import os
    from pathlib import Path
    
    try:
        from dotenv import load_dotenv
        if Path(".env").exists():
            load_dotenv(override=True)
            print("✅ Loaded .env file")
    except ImportError:
        print("⚠️  python-dotenv not available")
    
    # Set required variables
    required_vars = {
        "DB_HOST": "localhost",
        "SECRET_KEY": "dev-secret-12345", 
        "AUTH0_CLIENT_ID": "dev-client-id",
        "AUTH0_CLIENT_SECRET": "dev-client-secret",
        "AUTH0_DOMAIN": "dev.auth0.com",
        "AUTH0_AUDIENCE": "dev-audience",
        "YOSAI_ENV": "development"
    }
    
    for var, default in required_vars.items():
        if not os.getenv(var):
            os.environ[var] = default
    
    try:
        print("🚀 Testing your fixed app...")
        
        # Import your app factory  
        from core.app_factory import create_application
        
        app = create_application()
        if app:
            print("✅ App created successfully!")
            print("🎯 All JSON serialization issues appear to be resolved!")
            print("🌐 Starting on port 8053...")
            
            # Use the new API
            app.run(debug=True, host="127.0.0.1", port=8053)
        else:
            print("❌ Failed to create app")
            
    except Exception as e:
        print(f"❌ Error testing app: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main fix function"""
    print("🔧 Fixing Dash API Calls")
    print("=" * 25)
    
    fixes = fix_dash_api_calls()
    
    if fixes:
        print(f"\n✅ Fixed {len(fixes)} files:")
        for fix in fixes:
            print(f"   - {fix}")
        
        print(f"\n🚀 Now you can run:")
        print(f"   python3 debug_json_error.py")
        print(f"   python3 minimal_working_app.py")
        print(f"   python3 app.py")
        
        # Test the app
        response = input(f"\nTest your app now? [Y/n]: ").strip().lower()
        if response in ['', 'y', 'yes']:
            test_your_app()
    else:
        print("No files needed fixing")


if __name__ == "__main__":
    main()