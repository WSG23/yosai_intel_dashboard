"""Callback management for the dashboard"""
from typing import Any, Optional
import logging
from .component_registry import ComponentRegistry
from .layout_manager import LayoutManager

logger = logging.getLogger(__name__)


class CallbackManager:
    """Manages callback registration"""

    def __init__(
        self,
        app: Any,
        component_registry: ComponentRegistry,
        layout_manager: LayoutManager,
        container: Any,
    ):
        self.app = app
        self.registry = component_registry
        self.layout_manager = layout_manager
        self.container = container

    def register_all_callbacks(self) -> None:
        """Register all callbacks"""
        try:
            # Register page routing callback
            self._register_page_routing_callback()

            # Register component callbacks safely
            self._register_component_callbacks()

            # Register analytics callbacks
            self._register_analytics_callbacks()

            # Register navbar callback
            self._register_navbar_callback()

            logger.info("All callbacks registered successfully")

        except Exception as e:
            logger.error(f"Error registering callbacks: {e}")

    def _register_page_routing_callback(self) -> None:
        """Page routing callback"""
        try:
            from dash import Output, Input

            @self.app.callback(
                Output("page-content", "children"),
                Input("url", "pathname"),
                prevent_initial_call=False,
            )
            def display_page(pathname: Optional[str]) -> Any:
                """Route to appropriate page content"""
                try:
                    if pathname == "/analytics":
                        return self._handle_analytics_page()
                    else:
                        # Default to dashboard
                        return self.layout_manager.create_dashboard_content()

                except Exception as e:
                    logger.error(f"Error in page routing: {e}")
                    return self._create_error_page(f"Page routing error: {str(e)}")

        except ImportError:
            logger.error("Cannot register page routing - Dash not available")

    def _handle_analytics_page(self) -> Any:
        """Handle analytics page"""
        analytics_module = self.registry.get_component("analytics_module")

        if analytics_module is not None:
            layout_func = getattr(analytics_module, "layout", None)
            if layout_func is not None and callable(layout_func):
                try:
                    return layout_func()
                except Exception as e:
                    logger.error(f"Error creating analytics layout: {e}")
                    return self._create_error_page(
                        f"Error loading analytics page: {str(e)}"
                    )

        return self._create_error_page("Analytics page not available")

    def _register_component_callbacks(self) -> None:
        """Register callbacks for individual components"""
        try:
            # Map panel callbacks
            map_callbacks = self.registry.get_component("map_panel_callbacks")
            if map_callbacks and callable(map_callbacks):
                try:
                    map_callbacks(self.app)
                    logger.info("Map panel callbacks registered")
                except Exception as e:
                    logger.error(f"Error registering map callbacks: {e}")

        except Exception as e:
            logger.error(f"Error in component callback registration: {e}")

    def _register_analytics_callbacks(self) -> None:
        """Register analytics callbacks"""
        try:
            analytics_module = self.registry.get_component("analytics_module")
            if analytics_module:
                register_func = getattr(analytics_module, "register_callbacks", None)
                if register_func and callable(register_func):
                    try:
                        register_func(self.app)
                        logger.info("Analytics callbacks registered")
                    except Exception as e:
                        logger.error(f"Error registering analytics callbacks: {e}")

        except Exception as e:
            logger.error(f"Error in analytics callback registration: {e}")

    def _register_navbar_callback(self) -> None:
        """Register navbar callbacks"""
        try:
            navbar_callbacks = self.registry.get_component("navbar_callbacks")
            if navbar_callbacks and callable(navbar_callbacks):
                try:
                    navbar_callbacks(self.app)
                    logger.info("Navbar callbacks registered")
                except Exception as e:
                    logger.error(f"Error registering navbar callbacks: {e}")

        except Exception as e:
            logger.error(f"Error in navbar callback registration: {e}")

    def _create_error_page(self, error_message: str) -> Any:
        """Create error page"""
        try:
            from dash import html
            import dash_bootstrap_components as dbc
            
            return dbc.Container([
                dbc.Alert([
                    html.H4("⚠️ Error", className="alert-heading"),
                    html.P(error_message),
                ], color="danger"),
                dbc.Button("← Back to Dashboard", href="/", color="primary")
            ])
        except ImportError:
            return f"Error: {error_message}"
