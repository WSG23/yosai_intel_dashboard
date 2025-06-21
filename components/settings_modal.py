"""Settings Modal Component"""
from dash import html, clientside_callback, Input, Output
import dash
from typing import Any
import logging

logger = logging.getLogger(__name__)

# Safe import handling
try:
    from dash import dcc
    DASH_AVAILABLE = True
except ImportError:
    logger.warning("Dash not available for settings modal")
    DASH_AVAILABLE = False


def create_settings_modal() -> html.Div:
    """Create the settings modal component"""

    if not DASH_AVAILABLE:
        return html.Div("Settings modal not available")

    settings_items = [
        {"icon": "/assets/navbar_icons/upload.png", "text": "Critical Doors", "id": "critical-doors"},
        {"icon": "/assets/navbar_icons/upload.png", "text": "Event Reason Aliases", "id": "event-aliases"},
        {"icon": "/assets/navbar_icons/upload.png", "text": "Insights Settings", "id": "insights-settings"},
        {"icon": "/assets/navbar_icons/upload.png", "text": "Learning Rate", "id": "learning-rate"},
        {"icon": "/assets/navbar_icons/settings.png", "text": "Manage Auth", "id": "manage-auth"},
        {"icon": "/assets/navbar_icons/upload.png", "text": "Resolution Tags", "id": "resolution-tags"},
        {"icon": "/assets/navbar_icons/upload.png", "text": "System Admin Tools", "id": "system-admin"},
        {"icon": "/assets/navbar_icons/upload.png", "text": "Ticket Criticality", "id": "ticket-criticality"},
        {"icon": "/assets/navbar_icons/upload.png", "text": "Ticket Generation", "id": "ticket-generation"},
        {"icon": "/assets/navbar_icons/settings.png", "text": "User Management", "id": "user-management"},
    ]

    try:
        modal_content = html.Div(
            [
                html.Div(
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("Settings", className="settings-modal-title"),
                                    html.Button(
                                        "×",
                                        id="settings-modal-close-btn",
                                        className="settings-modal-close",
                                    ),
                                ],
                                className="settings-modal-header",
                            ),
                            html.Div(
                                html.Ul(
                                    [
                                        html.Li(
                                            [
                                                html.Img(
                                                    src=item["icon"],
                                                    className="settings-item-icon",
                                                    alt="",
                                                ),
                                                html.Span(
                                                    item["text"],
                                                    className="settings-item-text",
                                                ),
                                            ],
                                            className="settings-item",
                                            id=f"settings-{item['id']}",
                                        )
                                        for item in settings_items
                                    ],
                                    className="settings-item-list",
                                ),
                                className="settings-modal-body",
                            ),
                        ],
                        className="settings-modal-content",
                    ),
                    className="settings-modal-overlay hidden",
                    id="settings-modal-overlay",
                )
            ],
            id="settings-modal-container",
        )

        return modal_content

    except Exception as e:
        logger.error(f"Error creating settings modal: {e}")
        return html.Div(f"Settings modal error: {e}", className="text-danger")


def register_settings_modal_callbacks(app):
    """Register callbacks for settings modal functionality"""

    if not DASH_AVAILABLE:
        return

    try:
        @app.callback(
            Output("settings-modal-overlay", "className"),
            [
                Input("navbar-settings-btn", "n_clicks"),
                Input("settings-modal-close-btn", "n_clicks"),
                Input("settings-modal-overlay", "n_clicks"),
            ],
            prevent_initial_call=True,
        )
        def _toggle_settings_modal(open_clicks, close_clicks, overlay_clicks):
            ctx = dash.callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if triggered_id == "navbar-settings-btn":
                return "settings-modal-overlay"
            return "settings-modal-overlay hidden"

        @app.callback(
            Output("url", "pathname"),
            [
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
            prevent_initial_call=True,
        )
        def handle_settings_navigation(*args):
            ctx = dash.callback_context
            if not ctx.triggered:
                return dash.no_update

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

    except Exception as e:
        logger.error(f"Error registering settings modal callbacks: {e}")


layout = create_settings_modal
__all__ = ["create_settings_modal", "register_settings_modal_callbacks", "layout"]
