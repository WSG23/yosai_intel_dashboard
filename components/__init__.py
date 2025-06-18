# components/__init__.py - FIXED: Remove circular imports
"""
Yōsai Intel Dashboard Components Package  
Safe component imports without circular dependencies
"""

# NOTE: navbar is in dashboard/layout/navbar.py, not here
# Import only components that actually exist in this directory

try:
    from . import map_panel
    print("✅ Imported map_panel")
except ImportError as e:
    print(f"⚠️  Could not import map_panel: {e}")
    map_panel = None

try:
    from . import bottom_panel
    print("✅ Imported bottom_panel")
except ImportError as e:
    print(f"⚠️  Could not import bottom_panel: {e}")
    bottom_panel = None

try:
    from . import incident_alerts_panel
    print("✅ Imported incident_alerts_panel")
except ImportError as e:
    print(f"⚠️  Could not import incident_alerts_panel: {e}")
    incident_alerts_panel = None

try:
    from . import weak_signal_panel
    print("✅ Imported weak_signal_panel")
except ImportError as e:
    print(f"⚠️  Could not import weak_signal_panel: {e}")
    weak_signal_panel = None

# Safe attribute access
def get_component_layout(component_name: str):
    """Safely get component layout"""
    component = globals().get(component_name)
    if component is not None:
        return getattr(component, 'layout', None)
    return None

# Export only components that actually exist
__all__ = [
    'map_panel', 'bottom_panel', 
    'incident_alerts_panel', 'weak_signal_panel',
    'get_component_layout'
]
