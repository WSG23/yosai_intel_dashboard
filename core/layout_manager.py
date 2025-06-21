"""Layout management for the dashboard"""
from typing import Any
import logging
from .component_registry import ComponentRegistry

logger = logging.getLogger(__name__)

# Safe import of Dash components at module level
try:
    from dash import html, dcc
    DASH_AVAILABLE = True
except ImportError:
    logger.warning("Dash components not available")
    DASH_AVAILABLE = False
    # Create fallback html and dcc objects
    class FallbackHtml:
        @staticmethod
        def Div(*args, **kwargs):
            return "Dashboard layout not available"
        
        @staticmethod
        def H1(*args, **kwargs):
            return "Title not available"
            
        @staticmethod
        def P(*args, **kwargs):
            return "Content not available"
    
    class FallbackDcc:
        @staticmethod
        def Location(*args, **kwargs):
            return "Location component not available"
    
    html = FallbackHtml()
    dcc = FallbackDcc()

class LayoutManager:
    """Manages layout creation"""
    
    def __init__(self, component_registry: ComponentRegistry):
        self.registry = component_registry
    
    def create_main_layout(self) -> Any:
        """Create main dashboard layout"""
        if not DASH_AVAILABLE:
            logger.error("Dash components not available for main layout")
            return "Dashboard not available - Dash components missing"
        
        try:
            # Main layout structure
            location_component = dcc.Location(id='url', refresh=False)
            navbar_component = self.registry.get_component_or_fallback(
                'navbar', 
                "Navigation not available"
            )
            content_component = html.Div(
                id='page-content', 
                children=[self.create_dashboard_content()]
            )
            
            return html.Div([
                location_component,
                navbar_component,
                content_component
            ], className="dashboard")
            
        except Exception as e:
            logger.error(f"Error creating main layout: {e}")
            # html is guaranteed to be available here since DASH_AVAILABLE is True
            return html.Div(f"Layout error: {str(e)}", className="alert alert-danger")
    
    def create_dashboard_content(self) -> Any:
        """Create dashboard content using specific component files"""
        if not DASH_AVAILABLE:
            logger.error("Dash components not available for dashboard content")
            return "Dashboard content not available"

        try:
            # LEFT PANEL: incident_alerts_panel.py
            left_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'incident_alerts',
                    "Incident Alerts Panel - Component not available"
                )
            ], className="left-panel")

            # MIDDLE PANEL: map_panel.py
            map_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'map_panel',
                    "Map Panel - Component not available"
                )
            ], className="map-panel")

            # RIGHT PANEL: weak_signal_panel.py
            right_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'weak_signal',
                    "Weak Signal Panel - Component not available"
                )
            ], className="right-panel")

            # TOP ROW: 3-column layout (left + middle + right)
            main_content = html.Div([
                left_panel,
                map_panel,
                right_panel,
            ], className="main-content")

            # BOTTOM PANEL: bottom_panel.py
            bottom_panel = self.registry.get_component_or_fallback(
                'bottom_panel',
                "Bottom Panel - Component not available"
            )

            return html.Div([main_content, bottom_panel])

        except Exception as e:
            logger.error(f"Error creating dashboard content: {e}")
            return html.Div(f"Dashboard content error: {str(e)}", className="alert alert-danger")
    
    def create_safe_fallback_layout(self) -> str:
        """Create a safe fallback layout when Dash is not available"""
        return """
        <div class="dashboard-fallback">
            <h1>🏯 Yōsai Intel Dashboard</h1>
            <p>Dashboard is running in safe mode</p>
            <p>Dash components are not available</p>
        </div>
        """

    def _get_navigation_items(self):
        """Get navigation items including new pages"""
        nav_items = [
            {"label": "Dashboard", "href": "/"},
            {"label": "File Upload", "href": "/file-upload"},
            {"label": "Deep Analytics", "href": "/analytics"},
        ]
        return nav_items
