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


layout = create_settings_modal
__all__ = ["create_settings_modal", "layout"]
