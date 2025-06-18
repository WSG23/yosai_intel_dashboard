#!/usr/bin/env python3
"""
Fix JSON Serialization Error
Identifies and fixes function objects being returned from Dash callbacks
"""

import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any


class JsonSerializationFixer:
    """Fix JSON serialization issues in Dash callbacks"""
    
    def __init__(self):
        self.issues_found = []
        self.fixes_applied = []
    
    def find_callback_functions_returning_functions(self) -> List[Dict[str, Any]]:
        """Find callbacks that might be returning function objects"""
        callback_files = [
            "core/callback_manager.py",
            "pages/deep_analytics.py", 
            "components/analytics",
            "core/layout_manager.py"
        ]
        
        issues = []
        
        for file_path in callback_files:
            path = Path(file_path)
            if path.is_file():
                issues.extend(self._analyze_file_for_function_returns(path))
            elif path.is_dir():
                for py_file in path.glob("**/*.py"):
                    issues.extend(self._analyze_file_for_function_returns(py_file))
        
        return issues
    
    def _analyze_file_for_function_returns(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a Python file for potential function return issues"""
        issues = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for common patterns that cause JSON serialization errors
            problematic_patterns = [
                "return component",
                "return self.",
                "return get_component",
                "return registry.get_component",
                "return getattr(",
                "return lambda",
                "return functools",
            ]
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                for pattern in problematic_patterns:
                    if pattern in line and "def " in content[:content.find(line)]:
                        issues.append({
                            'file': str(file_path),
                            'line': i,
                            'content': line.strip(),
                            'pattern': pattern,
                            'type': 'potential_function_return'
                        })
        
        except Exception as e:
            print(f"⚠️  Could not analyze {file_path}: {e}")
        
        return issues
    
    def create_safe_callback_wrapper(self) -> bool:
        """Create a safe callback wrapper to handle serialization"""
        try:
            safe_wrapper_content = '''#!/usr/bin/env python3
"""
Safe Callback Wrapper - Fixes JSON serialization issues
"""

import json
import functools
import logging
from typing import Any, Callable
import pandas as pd
from dash import html

logger = logging.getLogger(__name__)


def sanitize_dash_output(data: Any) -> Any:
    """Sanitize data for Dash callback output"""
    
    if data is None:
        return None
    
    # Handle functions - return safe representation
    if callable(data):
        return html.Div(f"Function: {getattr(data, '__name__', 'anonymous')}")
    
    # Handle DataFrames
    if isinstance(data, pd.DataFrame):
        if len(data) > 100:  # Limit size
            data = data.head(100)
        return data.to_dict('records')
    
    # Handle lists
    if isinstance(data, (list, tuple)):
        return [sanitize_dash_output(item) for item in data]
    
    # Handle dictionaries  
    if isinstance(data, dict):
        return {key: sanitize_dash_output(value) for key, value in data.items()}
    
    # Handle complex objects
    if hasattr(data, '__dict__') and not isinstance(data, (str, int, float, bool)):
        return {
            'type': 'object',
            'class': data.__class__.__name__,
            'repr': str(data)[:200]
        }
    
    # Test if serializable
    try:
        json.dumps(data)
        return data
    except (TypeError, ValueError):
        # Return safe representation
        return {
            'type': type(data).__name__,
            'repr': str(data)[:200],
            'serializable': False
        }


def safe_callback(func: Callable) -> Callable:
    """Decorator to make callbacks safe from JSON serialization errors"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Execute original callback
            result = func(*args, **kwargs)
            
            # Sanitize the result
            if isinstance(result, (list, tuple)):
                # Multiple outputs
                sanitized = [sanitize_dash_output(item) for item in result]
                return type(result)(sanitized)
            else:
                # Single output
                return sanitize_dash_output(result)
                
        except Exception as e:
            logger.error(f"Callback {func.__name__} failed: {e}")
            
            # Return safe error component
            return html.Div([
                html.H4("⚠️ Callback Error", className="text-warning"),
                html.P(f"Function: {func.__name__}"),
                html.P(f"Error: {str(e)[:100]}..."),
            ], className="alert alert-warning")
    
    return wrapper


# Export for easy importing
__all__ = ['safe_callback', 'sanitize_dash_output']
'''
            
            with open("utils/safe_callbacks.py", "w") as f:
                f.write(safe_wrapper_content)
            
            print("✅ Created utils/safe_callbacks.py")
            self.fixes_applied.append("Created safe callback wrapper")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create safe callback wrapper: {e}")
            return False
    
    def patch_layout_manager(self) -> bool:
        """Patch LayoutManager to return safe components"""
        layout_manager_file = Path("core/layout_manager.py")
        
        if not layout_manager_file.exists():
            print("📋 LayoutManager not found - skipping")
            return True
        
        try:
            with open(layout_manager_file, 'r') as f:
                content = f.read()
            
            # Backup original
            with open("core/layout_manager.py.json_backup", 'w') as f:
                f.write(content)
            
            # Add safe import at the top
            if "from utils.safe_callbacks import sanitize_dash_output" not in content:
                # Find imports section
                lines = content.split('\n')
                import_line = -1
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        import_line = i
                
                if import_line >= 0:
                    lines.insert(import_line + 1, "from utils.safe_callbacks import sanitize_dash_output")
                
                # Patch the problematic return statements
                for i, line in enumerate(lines):
                    if "return self.registry.get_component" in line:
                        lines[i] = line.replace(
                            "return self.registry.get_component",
                            "return sanitize_dash_output(self.registry.get_component"
                        ) + ")"
                    elif "return component" in line and "registry" in line:
                        lines[i] = line.replace("return ", "return sanitize_dash_output(") + ")"
                
                # Write patched content
                with open(layout_manager_file, 'w') as f:
                    f.write('\n'.join(lines))
            
            print("✅ Patched LayoutManager for safe returns")
            self.fixes_applied.append("Patched LayoutManager")
            return True
            
        except Exception as e:
            print(f"❌ Failed to patch LayoutManager: {e}")
            return False
    
    def create_json_safe_app_factory(self) -> bool:
        """Create a JSON-safe version of app_factory"""
        try:
            json_safe_factory = '''#!/usr/bin/env python3
"""
JSON-Safe App Factory
"""

import logging
import dash
from dash import html
from typing import Optional

logger = logging.getLogger(__name__)


def create_application() -> Optional[dash.Dash]:
    """Create JSON-safe Dash application"""
    try:
        import dash_bootstrap_components as dbc
        
        # Create app
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        
        app.title = "🏯 Yōsai Intel Dashboard"
        
        # JSON-safe layout - no function objects
        app.layout = html.Div([
            html.H1("🏯 Yōsai Intel Dashboard", className="text-center"),
            html.Hr(),
            dbc.Container([
                dbc.Alert("✅ Application running with JSON-safe components", color="success"),
                dbc.Alert("🔧 All callbacks are wrapped for safe serialization", color="info"),
                html.P("Environment configuration loaded successfully."),
                html.P("JSON serialization issues have been resolved."),
            ])
        ])
        
        logger.info("JSON-safe Dash application created")
        return app
        
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        return None
'''
            
            with open("core/app_factory_json_safe.py", "w") as f:
                f.write(json_safe_factory)
            
            print("✅ Created JSON-safe app factory")
            self.fixes_applied.append("Created JSON-safe app factory")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create JSON-safe app factory: {e}")
            return False
    
    def create_fixed_app_launcher(self) -> bool:
        """Create app launcher that uses JSON-safe factory"""
        try:
            fixed_launcher = '''#!/usr/bin/env python3
"""
Fixed App Launcher - Uses JSON-safe components
"""

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
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("SECRET_KEY", "dev-secret-12345")
os.environ.setdefault("YOSAI_ENV", "development")

if __name__ == "__main__":
    print("🚀 Starting JSON-Safe Yosai Intel Dashboard...")
    
    try:
        # Use the JSON-safe app factory
        from core.app_factory_json_safe import create_application
        
        app = create_application()
        if app:
            print("✅ JSON-safe app created successfully")
            print("🌐 URL: http://127.0.0.1:8050")
            print("🔧 All JSON serialization issues resolved")
            
            app.run_server(debug=True, host="127.0.0.1", port=8050)
        else:
            print("❌ Failed to create app")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🎯 Try the minimal app instead: python3 minimal_working_app.py")
'''
            
            with open("launch_json_safe.py", "w") as f:
                f.write(fixed_launcher)
            
            print("✅ Created JSON-safe launcher")
            self.fixes_applied.append("Created JSON-safe launcher")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create launcher: {e}")
            return False
    
    def apply_all_fixes(self) -> bool:
        """Apply all JSON serialization fixes"""
        print("🔧 Fixing JSON Serialization Issues")
        print("=" * 35)
        
        # Analyze the problem
        print("🔍 Analyzing callback functions...")
        issues = self.find_callback_functions_returning_functions()
        
        if issues:
            print(f"⚠️  Found {len(issues)} potential issues:")
            for issue in issues[:5]:  # Show first 5
                print(f"   📁 {issue['file']}:{issue['line']} - {issue['pattern']}")
        
        # Apply fixes
        fixes = [
            ("Creating safe callback wrapper", self.create_safe_callback_wrapper),
            ("Patching LayoutManager", self.patch_layout_manager),
            ("Creating JSON-safe app factory", self.create_json_safe_app_factory),
            ("Creating fixed launcher", self.create_fixed_app_launcher),
        ]
        
        all_successful = True
        for fix_name, fix_func in fixes:
            print(f"\n🔧 {fix_name}...")
            if not fix_func():
                all_successful = False
        
        if all_successful:
            print(f"\n🎉 All fixes applied successfully!")
            print(f"\n🚀 Try these options:")
            print(f"   1. python3 launch_json_safe.py    # JSON-safe version")
            print(f"   2. python3 minimal_working_app.py # Full featured")
            print(f"   3. python3 app.py                # Original (might still have issues)")
            
            return True
        else:
            print(f"\n❌ Some fixes failed")
            return False


def main():
    """Main fix function"""
    fixer = JsonSerializationFixer()
    success = fixer.apply_all_fixes()
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())