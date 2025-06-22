"""
Navigation Callback Manager for centralized page routing
"""
from dash import html, Input, Output
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)


class NavigationCallbackManager:
    """Manages navigation and page routing callbacks"""

    def __init__(self, callback_registry, layout_manager):
        self.registry = callback_registry
        self.layout_manager = layout_manager

    def register_all(self):
        """Register all navigation callbacks"""
        self._register_page_routing()
        self._register_navbar_callbacks()

    def _register_page_routing(self):
        """Register main page routing callback"""
        @self.registry.register_callback(
            outputs=Output("page-content", "children"),  # Single output, not list
            inputs=[Input("url", "pathname")],
            prevent_initial_call=False,
            callback_id="main_page_routing"
        )
        def display_page(pathname: Optional[str]) -> Any:
            """Route to appropriate page based on URL pathname"""
            try:
                from pages import get_page_layout

                # Route to appropriate page
                if pathname == "/" or pathname is None:
                    return self.layout_manager.create_dashboard_content()
                elif pathname == "/analytics":
                    layout_func = get_page_layout('deep_analytics')
                    if layout_func and callable(layout_func):
                        return layout_func()
                    else:
                        return self._create_error_page("Analytics page not available")
                elif pathname == "/file-upload":
                    layout_func = get_page_layout('file_upload')
                    if layout_func and callable(layout_func):
                        return layout_func()
                    else:
                        return self._create_error_page("File Upload page not available")
                elif pathname and pathname.startswith("/settings"):
                    return self._handle_settings_pages(pathname)
                else:
                    return self._create_404_page(pathname)
            except Exception as e:
                logger.error(f"Error in page routing for {pathname}: {e}")
                return self._create_error_page(f"Error loading page: {str(e)}")

    def _register_navbar_callbacks(self):
        """Register navbar-related callbacks"""
        # Live time update - single output, so don't use list wrapper
        @self.registry.register_callback(
            outputs=Output("live-time", "children"),  # Single output, not a list
            inputs=[Input("url", "pathname")],
            callback_id="navbar_live_time"
        )
        def update_live_time(pathname: str) -> str:
            """Update live time display"""
            try:
                import datetime
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return f"Live: {current_time}"
            except Exception as e:
                logger.error(f"Error updating live time: {e}")
                return "Live: --:--:--"

        # Page context update - single output, so don't use list wrapper
        @self.registry.register_callback(
            outputs=Output("page-context", "children"),  # Single output, not a list
            inputs=[Input("url", "pathname")],
            callback_id="navbar_page_context"
        )
        def update_page_context(pathname: str) -> str:
            """Update page context based on current route"""
            page_contexts = {
                "/": "Dashboard – Main Operations",
                "/analytics": "Analytics – Data Intelligence",
                "/file-upload": "File Upload – Data Management",
                "/export": "Export – Report Generation",
                "/settings": "Settings – System Configuration",
                "/login": "Login – Authentication"
            }
            return page_contexts.get(pathname, "Dashboard – Main Operations")

    def _handle_settings_pages(self, pathname: str) -> Any:
        """Handle settings sub-pages"""
        try:
            return html.Div([
                html.H1("Settings", className="page-title"),
                html.P(f"Settings page: {pathname}", className="text-gray-400"),
                html.P("Settings functionality will be implemented here.", className="text-gray-400")
            ])
        except Exception as e:
            logger.error(f"Error creating settings page: {e}")
            return self._create_error_page("Settings page error")

    def _create_404_page(self, pathname: str) -> Any:
        """Create 404 page"""
        try:
            return html.Div([
                html.H1("404 - Page Not Found", className="text-2xl font-bold text-red-500"),
                html.P(f"The page '{pathname}' was not found.", className="text-gray-400 mt-4"),
                html.A("← Back to Dashboard", href="/", className="text-blue-400 hover:text-blue-300 mt-4 inline-block")
            ], className="p-8 text-center")
        except Exception:
            return f"404 - Page '{pathname}' not found"

    def _create_error_page(self, error_message: str) -> Any:
        """Create error page"""
        try:
            return html.Div([
                html.H1("⚠️ Error", className="text-2xl font-bold text-red-500"),
                html.P(error_message, className="text-gray-400 mt-4"),
                html.A("← Back to Dashboard", href="/", className="text-blue-400 hover:text-blue-300 mt-4 inline-block")
            ], className="p-8 text-center")
        except Exception:
            return f"Error: {error_message}"
