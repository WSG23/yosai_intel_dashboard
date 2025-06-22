"""
Settings Modal Callback Manager
"""
from dash import Input, Output, callback_context
import dash
import logging

logger = logging.getLogger(__name__)


class SettingsCallbackManager:
    """Callback manager for settings modal"""

    def __init__(self, callback_registry):
        self.registry = callback_registry

    def register_all(self):
        """Register all settings callbacks"""
        self._register_modal_visibility()
        self._register_settings_navigation()

    def _register_modal_visibility(self):
        """Register settings modal visibility callback"""
        @self.registry.register_callback(
            outputs=[Output("settings-modal-overlay", "className")],
            inputs=[
                Input("navbar-settings-btn", "n_clicks"),
                Input("settings-modal-close-btn", "n_clicks"),
                Input("settings-modal-overlay", "n_clicks"),
            ],
            states=[],
            callback_id="settings_modal_visibility",
        )
        def toggle_settings_modal(open_clicks, close_clicks, overlay_clicks):
            """Toggle settings modal visibility"""
            ctx = callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if triggered_id == "navbar-settings-btn":
                return "settings-modal-overlay"
            return "settings-modal-overlay hidden"

    def _register_settings_navigation(self):
        """Register settings navigation callbacks"""
        @self.registry.register_callback(
            outputs=[Output("url", "pathname")],
            inputs=[
                Input("settings-critical-doors", "n_clicks"),
                Input("settings-event-aliases", "n_clicks"),
                Input("settings-insights-settings", "n_clicks"),
                Input("settings-learning-rate", "n_clicks"),
                Input("settings-manage-auth", "n_clicks"),
                Input("settings-resolution-tags", "n_clicks"),
                Input("settings-system-admin", "n_clicks"),
                Input("settings-ticket-criticality", "n_clicks"),
                Input("settings-ticket-generation", "n_clicks"),
                Input("settings-user-management", "n_clicks"),
            ],
            callback_id="settings_navigation",
        )
        def handle_settings_navigation(*args):
            """Handle settings navigation"""
            ctx = callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            settings_routes = {
                "settings-critical-doors": "/settings/critical-doors",
                "settings-event-aliases": "/settings/event-aliases",
                "settings-insights-settings": "/settings/insights",
                "settings-learning-rate": "/settings/learning-rate",
                "settings-manage-auth": "/settings/auth",
                "settings-resolution-tags": "/settings/resolution-tags",
                "settings-system-admin": "/settings/admin",
                "settings-ticket-criticality": "/settings/ticket-criticality",
                "settings-ticket-generation": "/settings/ticket-generation",
                "settings-user-management": "/settings/users",
            }

            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
            return settings_routes.get(triggered_id, dash.no_update)
