# core/layout_manager.py - CLEAN VERSION
"""Layout management with safe component handling"""
from typing import Any
import logging

logger = logging.getLogger(__name__)


class LayoutManager:
    """Manages layout creation with safe component handling"""
    
    def __init__(self, component_registry):
        self.registry = component_registry
    
    def create_main_layout(self) -> Any:
        """Create main layout with safe components"""
        try:
            from dash import html, dcc
            
            # Create safe location component
            location_component = dcc.Location(id='url', refresh=False)
            
            # Get navbar safely
            navbar_component = self._get_safe_component('navbar', 'Navigation not available')
            
            # Create content area
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
        except Exception as e:
            logger.error(f"Error creating main layout: {e}")
            return None
    
    def create_dashboard_content(self) -> Any:
        """Create dashboard content with safe components"""
        try:
            from dash import html
            
            # Left panel with safe components
            left_panel = html.Div([
                self._get_safe_component('incident_alerts', 'Incident Alerts - Component not available')
            ], className="dashboard__left-panel")
            
            # Map panel with safe components  
            map_panel = html.Div([
                self._get_safe_component('map_panel', 'Map Panel - Component not available')
            ], className="dashboard__map-panel")
            
            # Bottom panel with safe components
            bottom_panel = html.Div([
                self._get_safe_component('bottom_panel', 'Bottom Panel - Component not available')
            ], className="dashboard__bottom-panel")
            
            return html.Div([
                html.Div([left_panel, map_panel], className="dashboard__top-row"),
                bottom_panel
            ], className="dashboard__content")
            
        except Exception as e:
            logger.error(f"Error creating dashboard content: {e}")
            try:
                from dash import html
                return html.Div([
                    html.H3("🏯 Yōsai Intel Dashboard"),
                    html.P("Dashboard running in safe mode"),
                    html.P(f"Error: {str(e)}")
                ], className="container")
            except ImportError:
                return None
    
    def _get_safe_component(self, component_name: str, fallback_text: str) -> Any:
        """Safely get a component, handling functions and fallbacks"""
        try:
            # Try to get component from registry
            component = self.registry.get_component(component_name)
            
            # If it's a function, call it to get the actual component
            if callable(component):
                try:
                    component = component()
                except Exception as e:
                    logger.warning(f"Error calling component function {component_name}: {e}")
                    component = None
            
            # If we have a valid component, return it
            if component is not None:
                return component
            
            # Otherwise, return safe fallback
            return self._create_fallback_component(fallback_text)
            
        except Exception as e:
            logger.error(f"Error getting component {component_name}: {e}")
            return self._create_fallback_component(f"{fallback_text} (Error: {str(e)})")
    
    def _create_fallback_component(self, text: str) -> Any:
        """Create a safe fallback component"""
        try:
            from dash import html
            return html.Div(
                text,
                className="alert alert-warning text-center",
                style={"margin": "1rem", "padding": "1rem"}
            )
        except ImportError:
            # Ultimate fallback
            return text
