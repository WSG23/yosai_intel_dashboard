#!/usr/bin/env python3
"""Layout management integrated with DI container and services"""
from typing import Any, Union
import logging

logger = logging.getLogger(__name__)

# Safe import of Dash components with proper type handling
try:
    from dash import html, dcc
    DASH_AVAILABLE = True
    HtmlType = Any  # html module type
    DccType = Any   # dcc module type
except ImportError:
    logger.warning("Dash components not available")
    DASH_AVAILABLE = False
    HtmlType = None
    DccType = None
    html = None
    dcc = None


class LayoutManager:
    """Layout manager that uses DI container for service resolution"""

    def __init__(self, component_registry, container=None):
        self.registry = component_registry
        self.container = container

    def create_main_layout(self) -> Union[Any, str]:
        """Create main layout using services from DI container"""
        if not DASH_AVAILABLE or html is None or dcc is None:
            logger.error("Dash components not available")
            return "Dashboard not available - Dash components missing"

        try:
            # Create layout components
            location_component = dcc.Location(id='url', refresh=False)

            # Get navbar from DI container via registry
            navbar_component = self.registry.get_component_or_fallback(
                'navbar',
                "Navigation not available"
            )

            # Create content area that will be populated by routing
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
            if html is not None:
                return html.Div(f"Layout error: {str(e)}", className="alert alert-danger")
            else:
                return f"Layout error: {str(e)}"

    def create_dashboard_content(self) -> Union[Any, str]:
        """Create dashboard content using DI container services"""
        if not DASH_AVAILABLE or html is None:
            return "Dashboard content not available"

        try:
            # Use analytics service if available for data-driven panels
            analytics_service = None
            if self.container:
                try:
                    analytics_service = self.container.get_optional('analytics_service')
                except Exception:
                    logger.info("Analytics service not available")

            # Create panels using registry (which uses DI container)
            left_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'incident_alerts',
                    "Incident Alerts - Loading..."
                )
            ], className="left-panel")

            map_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'map_panel',
                    "Map Panel - Loading..."
                )
            ], className="map-panel")

            right_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'weak_signal',
                    "Weak Signal Panel - Loading..."
                )
            ], className="right-panel")

            # Main content with 3-column layout
            main_content = html.Div([
                left_panel,
                map_panel,
                right_panel,
            ], className="main-content")

            # Bottom panel
            bottom_panel = html.Div([
                self.registry.get_component_or_fallback(
                    'bottom_panel',
                    "Bottom Panel - Loading..."
                )
            ], className="bottom-panel-container")

            return html.Div([
                main_content,
                bottom_panel
            ], className="dashboard-layout")

        except Exception as e:
            logger.error(f"Error creating dashboard content: {e}")
            if html is not None:
                return html.Div([
                    html.H3("🏯 Yōsai Intel Dashboard"),
                    html.P("Dashboard running in safe mode"),
                    html.P(f"Error: {str(e)}")
                ], className="container")
            else:
                return "Dashboard content error"

