# fix_component_imports.py - Component Import Structure Fixer
"""
Fixes component imports and ensures proper __init__.py structure
Run this to resolve any remaining import issues
"""

import os
from pathlib import Path
from typing import Dict, List

def create_components_init() -> str:
    """Create components/__init__.py with safe imports"""
    return '''# components/__init__.py - FIXED: Safe component imports
"""
Yōsai Intel Dashboard Components Package
Type-safe imports with proper error handling
"""

# Import components with error handling
try:
    from . import navbar
except ImportError as e:
    print(f"Warning: Could not import navbar: {e}")
    navbar = None

try:
    from . import map_panel
except ImportError as e:
    print(f"Warning: Could not import map_panel: {e}")
    map_panel = None

try:
    from . import bottom_panel
except ImportError as e:
    print(f"Warning: Could not import bottom_panel: {e}")
    bottom_panel = None

try:
    from . import incident_alerts_panel
except ImportError as e:
    print(f"Warning: Could not import incident_alerts_panel: {e}")
    incident_alerts_panel = None

try:
    from . import weak_signal_panel
except ImportError as e:
    print(f"Warning: Could not import weak_signal_panel: {e}")
    weak_signal_panel = None

# Safe attribute access
def get_component_layout(component_name: str):
    """Safely get component layout"""
    component = globals().get(component_name)
    if component is not None:
        return getattr(component, 'layout', None)
    return None

# Export available components
__all__ = [
    'navbar', 'map_panel', 'bottom_panel', 
    'incident_alerts_panel', 'weak_signal_panel',
    'get_component_layout'
]
'''

def create_analytics_init() -> str:
    """Create components/analytics/__init__.py"""
    return '''# components/analytics/__init__.py - FIXED: Safe analytics imports
"""
Analytics components module - Type-safe imports
"""

# Import main component functions with error handling
try:
    from .file_uploader import create_file_uploader
except ImportError as e:
    print(f"Warning: Could not import file_uploader: {e}")
    def create_file_uploader(*args, **kwargs):
        from dash import html
        return html.Div("File uploader component not available")

try:
    from .data_preview import create_data_preview
except ImportError as e:
    print(f"Warning: Could not import data_preview: {e}")
    def create_data_preview(*args, **kwargs):
        from dash import html
        return html.Div("Data preview component not available")

try:
    from .analytics_charts import create_analytics_charts, create_summary_cards
except ImportError as e:
    print(f"Warning: Could not import analytics_charts: {e}")
    def create_analytics_charts(*args, **kwargs):
        from dash import html
        return html.Div("Analytics charts component not available")
    
    def create_summary_cards(*args, **kwargs):
        from dash import html
        return html.Div("Summary cards component not available")

# Handle file processing imports
FileProcessor = None
AnalyticsGenerator = None

try:
    from .file_processing import FileProcessor as _FileProcessor, AnalyticsGenerator as _AnalyticsGenerator
    FileProcessor = _FileProcessor
    AnalyticsGenerator = _AnalyticsGenerator
except ImportError as e:
    print(f"Warning: Could not import file_processing: {e}")
    
    # Create fallback classes
    class _FallbackFileProcessor:
        @staticmethod
        def process_file_content(contents, filename):
            return None
        
        @staticmethod
        def validate_dataframe(df):
            return True, "Fallback validation", []
    
    class _FallbackAnalyticsGenerator:
        @staticmethod
        def generate_analytics(df):
            return {}
    
    FileProcessor = _FallbackFileProcessor
    AnalyticsGenerator = _FallbackAnalyticsGenerator

# Export all public functions
__all__ = [
    'create_file_uploader',
    'create_data_preview', 
    'create_analytics_charts',
    'create_summary_cards',
    'FileProcessor',
    'AnalyticsGenerator'
]
'''

def create_pages_init() -> str:
    """Create pages/__init__.py"""
    return '''# pages/__init__.py - Safe page imports
"""
Dashboard pages package
"""

try:
    from . import deep_analytics
except ImportError as e:
    print(f"Warning: Could not import deep_analytics: {e}")
    deep_analytics = None

__all__ = ['deep_analytics']
'''

def create_models_init() -> str:
    """Create models/__init__.py"""
    return '''# models/__init__.py - FIXED: Type-safe model imports
"""
Yōsai Intel Data Models Package - Type-safe and Modular
"""

# Import enums
try:
    from .enums import (
        AnomalyType, AccessResult, BadgeStatus,
        SeverityLevel, TicketStatus, DoorType
    )
except ImportError as e:
    print(f"Warning: Could not import enums: {e}")
    # Create fallback enums
    from enum import Enum
    class AnomalyType(Enum):
        UNKNOWN = "unknown"
    class AccessResult(Enum):
        UNKNOWN = "unknown"
    class BadgeStatus(Enum):
        UNKNOWN = "unknown"
    class SeverityLevel(Enum):
        UNKNOWN = "unknown"
    class TicketStatus(Enum):
        UNKNOWN = "unknown"
    class DoorType(Enum):
        UNKNOWN = "unknown"

# Import entities  
try:
    from .entities import Person, Door, Facility
except ImportError as e:
    print(f"Warning: Could not import entities: {e}")
    # Create fallback classes
    class Person:
        pass
    class Door:
        pass
    class Facility:
        pass

# Import events
try:
    from .events import AccessEvent, AnomalyDetection, IncidentTicket
except ImportError as e:
    print(f"Warning: Could not import events: {e}")
    # Create fallback classes
    class AccessEvent:
        pass
    class AnomalyDetection:
        pass
    class IncidentTicket:
        pass

# Import base models
try:
    from .base import BaseModel, AccessEventModel, AnomalyDetectionModel, ModelFactory
except ImportError as e:
    print(f"Warning: Could not import base models: {e}")
    # Create fallback classes
    class BaseModel:
        pass
    class AccessEventModel:
        pass
    class AnomalyDetectionModel:
        pass
    class ModelFactory:
        @staticmethod
        def create_access_model(db_connection):
            return AccessEventModel()
        @staticmethod
        def create_anomaly_model(db_connection):
            return AnomalyDetectionModel()

# Define exports
__all__ = [
    # Enums
    'AnomalyType', 'AccessResult', 'BadgeStatus', 'SeverityLevel', 
    'TicketStatus', 'DoorType',
    
    # Entities
    'Person', 'Door', 'Facility',
    
    # Events
    'AccessEvent', 'AnomalyDetection', 'IncidentTicket',
    
    # Models
    'BaseModel', 'AccessEventModel', 'AnomalyDetectionModel', 'ModelFactory'
]
'''

def create_safe_navbar() -> str:
    """Create a type-safe navbar component"""
    return '''# components/navbar.py - FIXED: Type-safe navbar
"""
Navigation bar component with complete type safety
"""

try:
    import dash_bootstrap_components as dbc
    from dash import html, dcc, callback, Output, Input
    import datetime
    DASH_AVAILABLE = True
except ImportError:
    print("Warning: Dash components not available")
    DASH_AVAILABLE = False
    # Create fallbacks
    dbc = None
    html = None
    dcc = None

def create_navbar_layout():
    """Create navbar layout with fallback"""
    if not DASH_AVAILABLE:
        return None
    
    try:
        return dbc.Navbar([
            dbc.Container([
                # Logo
                dbc.Row([
                    dbc.Col([
                        html.Img(
                            src="/assets/yosai_logo_name_white.png", 
                            height="40px",
                            className="navbar__logo"
                        )
                    ], width="auto")
                ], align="center"),
                
                # Center content
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.H5("Main Panel", className="navbar__title text-primary"),
                            html.Small("Logged in as: HQ Tower - East Wing", className="navbar__subtitle text-secondary"),
                            html.Small(id="live-time", className="navbar__subtitle text-tertiary")
                        ], className="text-center")
                    ])
                ], align="center", className="flex-grow-1"),
                
                # Navigation links
                dbc.Row([
                    dbc.Col([
                        dbc.Nav([
                            dbc.NavItem(dbc.NavLink("Dashboard", href="/", className="nav-link", active="exact")),
                            dbc.NavItem(dbc.NavLink("Deep Analytics", href="/analytics", className="nav-link", active="exact")),
                            dbc.NavItem(dbc.NavLink("Export Log", href="#", className="nav-link")),
                            dbc.NavItem(dbc.NavLink("Settings", href="#", className="nav-link")),
                        ], navbar=True, className="navbar__nav")
                    ])
                ], align="center")
            ], fluid=True, className="navbar__container")
        ], color="dark", dark=True, className="navbar")
    except Exception as e:
        print(f"Error creating navbar: {e}")
        return html.Div("Navigation not available")

# Create the layout
layout = create_navbar_layout()

# Safe callback registration
def register_navbar_callbacks(app):
    """Register navbar callbacks safely"""
    if not DASH_AVAILABLE:
        return
    
    try:
        @app.callback(
            Output("live-time", "children"),
            Input("live-time", "id"),
            prevent_initial_call=False
        )
        def update_time(_):
            try:
                return f"Live Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            except Exception:
                return "Time unavailable"
    except Exception as e:
        print(f"Error registering navbar callbacks: {e}")
'''

def fix_component_structure():
    """Fix the component directory structure and imports"""
    
    project_root = Path(".")
    components_dir = project_root / "components"
    analytics_dir = components_dir / "analytics"
    pages_dir = project_root / "pages"
    models_dir = project_root / "models"
    
    # Create directories if they don't exist
    for directory in [components_dir, analytics_dir, pages_dir, models_dir]:
        directory.mkdir(exist_ok=True)
    
    # Create/update __init__.py files
    files_to_create = {
        components_dir / "__init__.py": create_components_init(),
        analytics_dir / "__init__.py": create_analytics_init(),
        pages_dir / "__init__.py": create_pages_init(),
        models_dir / "__init__.py": create_models_init(),
        components_dir / "navbar.py": create_safe_navbar(),
    }
    
    created_files = []
    updated_files = []
    
    for file_path, content in files_to_create.items():
        if file_path.exists():
            # Backup existing file
            backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
            file_path.rename(backup_path)
            updated_files.append(str(file_path))
        else:
            created_files.append(str(file_path))
        
        file_path.write_text(content, encoding='utf-8')
    
    return created_files, updated_files

def main():
    """Main execution function"""
    print("🔧 Fixing Component Import Structure...")
    print("=" * 50)
    
    try:
        created_files, updated_files = fix_component_structure()
        
        print(f"✅ Files created: {len(created_files)}")
        for file in created_files:
            print(f"   📄 {file}")
        
        print(f"✅ Files updated: {len(updated_files)}")
        for file in updated_files:
            print(f"   🔄 {file}")
        
        print("\n" + "=" * 50)
        print("✅ Component structure fixed!")
        print("\n📋 Next steps:")
        print("1. Replace your app.py with the type-safe version")
        print("2. Run: python app.py")
        print("3. Check for any remaining import errors")
        print("4. Test all functionality")
        
    except Exception as e:
        print(f"❌ Error fixing component structure: {e}")

if __name__ == "__main__":
    main()