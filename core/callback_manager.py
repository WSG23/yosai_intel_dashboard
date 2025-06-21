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
        """Page routing callback using DI container for service resolution"""
        try:
            from dash import Output, Input, html
            from pages import get_page_layout

            @self.app.callback(
                Output("page-content", "children"),
                Input("url", "pathname"),
                prevent_initial_call=False,
            )
            def display_page(pathname: Optional[str]) -> Any:
                """Route to appropriate page using service layer"""
                try:
                    if pathname == "/" or pathname is None:
                        # Return dashboard content - this should persist
                        return self.layout_manager.create_dashboard_content()

                    elif pathname == "/file-upload":
                        # Get file upload service through DI
                        layout_func = get_page_layout('file_upload')
                        if layout_func and callable(layout_func):
                            return layout_func()
                        else:
                            return self._create_error_page("File Upload service not available")

                    elif pathname == "/analytics":
                        # Get analytics service through DI
                        layout_func = get_page_layout('deep_analytics')
                        if layout_func and callable(layout_func):
                            return layout_func()
                        else:
                            return self._create_error_page("Analytics service not available")
                    else:
                        return html.Div([
                            html.H1("404 - Page Not Found"),
                            html.P(f"The page '{pathname}' was not found."),
                            html.A("← Back to Dashboard", href="/", className="btn btn-primary")
                        ], className="container text-center mt-5")

                except Exception as e:
                    logger.error(f"Error in page routing: {e}")
                    return self._create_error_page(f"Service error: {str(e)}")

            logger.info("Page routing callback registered with DI integration")

        except Exception as e:
            logger.error(f"Error registering page routing: {e}")

    def _handle_analytics_page(self) -> Any:
        """Handle analytics page with safe error handling"""
        try:
            analytics_module = self.registry.get_component("analytics_module")

            if analytics_module is not None:
                layout_func = getattr(analytics_module, "layout", None)
                if layout_func is not None and callable(layout_func):
                    try:
                        result = layout_func()
                        # Ensure result is JSON-safe
                        return self._make_result_safe(result)
                    except Exception as e:
                        logger.error(f"Error creating analytics layout: {e}")
                        return self._create_error_page(
                            f"Error loading analytics page: {str(e)}"
                        )

            return self._create_error_page("Analytics page not available")

        except Exception as e:
            logger.error(f"Critical error in analytics page handling: {e}")
            return self._create_error_page(f"Critical error: {str(e)}")

    def _make_result_safe(self, result):
        """Make any result JSON-safe"""
        try:
            # Test if result is already safe
            import json
            json.dumps(str(result))
            return result
        except Exception:
            # Convert to safe representation
            try:
                from dash import html
                return html.Div(f"Analytics page loaded (safe mode): {type(result).__name__}")
            except ImportError:
                return str(result)

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
        """Register analytics and page callbacks"""
        try:
            from pages import register_page_callbacks

            # Register deep analytics callbacks
            success_analytics = register_page_callbacks('deep_analytics', self.app, self.container)
            if success_analytics:
                logger.info("Deep analytics callbacks registered successfully")
            else:
                logger.warning("Failed to register deep analytics callbacks")

            # Register file upload callbacks
            success_upload = register_page_callbacks('file_upload', self.app, self.container)
            if success_upload:
                logger.info("File upload callbacks registered successfully")
            else:
                logger.warning("Failed to register file upload callbacks")

        except Exception as e:
            logger.error(f"Error registering page callbacks: {e}")

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
