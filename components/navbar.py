"""Navbar component wrapper - Plugin integration."""

try:
    from dashboard.layout.navbar import create_plugin, create_navbar_layout, register_navbar_callbacks
    
    # Create plugin instance
    _navbar_plugin = create_plugin()
    
    def create_navbar():
        """Create navbar using plugin"""
        return _navbar_plugin.create_navbar_layout()
    
    # Export plugin functions
    layout = create_navbar_layout
    
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import navbar plugin: {e}")
    
    def create_navbar():
        return "Navbar plugin unavailable"
    
    def create_navbar_layout():
        return "Navbar plugin unavailable"
    
    def register_navbar_callbacks(app):
        pass
    
    layout = create_navbar_layout

__all__ = ["create_navbar", "layout", "register_navbar_callbacks"]
