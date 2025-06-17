# core/layout_manager.py
"""Layout management extracted from DashboardApp class"""
from typing import Any
import logging
from .component_registry import ComponentRegistry

logger = logging.getLogger(__name__)

class LayoutManager:
    """Manages layout creation - extracted from DashboardApp.create_main_layout()"""
    
    def __init__(self, component_registry: ComponentRegistry):
        self.registry = component_registry
    
    def create_main_layout(self) -> Any:
        """Create main layout - extracted from your DashboardApp.create_main_layout()"""
        try:
            from dash import html, dcc
            
            # Extract your existing location/navbar/content logic
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
            
        except ImportError:
            logger.error("Dash components not available")
            return None
    
    def create_dashboard_content(self) -> Any:
        """Create dashboard content - extracted from DashboardApp.create_dashboard_content()"""
        try:
            from dash import html
            
            # Extract your existing dashboard grid logic
            left_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'incident_alerts',
                    "Incident Alerts Panel - Component not available"
                )
            ], className="dashboard__left-panel")
            
            map_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'map_panel',
                    "Map Panel - Component not available"
                )
            ], className="dashboard__map-panel")
            
            right_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'weak_signal',
                    "Weak Signal Feed - Component not available"
                )
            ], className="dashboard__right-panel")
            
            content_grid = html.Div([
                left_panel,
                map_panel,
                right_panel,
            ], className="dashboard__content")
            
            bottom_panel = self.registry.get_component_or_fallback(
                'bottom_panel',
                "Bottom Panel - Component not available"
            )
            
            return html.Div([content_grid, bottom_panel])
            
        except ImportError:
            logger.error("HTML components not available")
            return None
