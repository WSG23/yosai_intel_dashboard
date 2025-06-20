"""
Navigation bar component with grid layout using existing framework
"""

import datetime
from typing import TYPE_CHECKING
from flask_babel import lazy_gettext as _l
from core.plugins.decorators import safe_callback

if TYPE_CHECKING:
    import dash_bootstrap_components as dbc
    from dash import html, dcc, callback, Output, Input

try:
    import dash_bootstrap_components as dbc
    from dash import html, dcc, callback, Output, Input

    DASH_AVAILABLE = True
except ImportError:
    print("Warning: Dash components not available")
    DASH_AVAILABLE = False
    dbc = None
    html = None
    dcc = None
    callback = None
    Output = None
    Input = None


def create_navbar_layout():
    """Create navbar layout with responsive grid design"""
    if not DASH_AVAILABLE:
        return None

    try:
        return dbc.Navbar(
            [
                dbc.Container(
                    [
                        dcc.Location(id="url-i18n"),
                        # Grid container using existing Bootstrap classes
                        dbc.Row(
                            [
                                # Left Column: Logo Area (clickable)
                                dbc.Col(
                                    [
                                        html.A(
                                            html.Img(
                                                src="/assets/yosai_logo_name_white.png",
                                                height="45px",
                                                className="navbar__logo",
                                            ),
                                            href="/",
                                            style={"text-decoration": "none"}
                                        )
                                    ],
                                    width=3,
                                    className="d-flex align-items-center pl-4",
                                ),

                                # Center Column: Main Panel Label & Context
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.Div(
                                                    "Main Panel:",
                                                    className="navbar-title text-center text-secondary",
                                                ),
                                                html.Div(
                                                    id="page-context",
                                                    children="Tokyo HQ – East Wing",
                                                    className="text-center text-secondary text-sm font-weight-bold",
                                                ),
                                                html.Div(
                                                    [
                                                        html.Span(
                                                            "Logged in as: HQ Tower – East Wing",
                                                            className="text-xs text-tertiary"
                                                        ),
                                                        html.Span(
                                                            [
                                                                html.Span("🟢", className="ml-2"),
                                                                html.Span(
                                                                    id="live-time",
                                                                    children="Live: 2025-06-20 09:55:54",
                                                                    className="ml-1"
                                                                )
                                                            ],
                                                            className="text-xs text-tertiary"
                                                        )
                                                    ],
                                                    className="d-flex align-items-center justify-content-center mt-1",
                                                )
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    width=6,
                                    className="d-flex align-items-center justify-content-center",
                                ),

                                # Right Column: Navigation Icons + Language Toggle
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                # Navigation Icons
                                                html.Div(
                                                    [
                                                        html.A(
                                                            html.Img(
                                                                src="/assets/navbar_icons/dashboard.png",
                                                                className="navbar-icon",
                                                                alt="Dashboard"
                                                            ),
                                                            href="/",
                                                            className="navbar-nav-link",
                                                            title="Dashboard"
                                                        ),
                                                        html.A(
                                                            html.Img(
                                                                src="/assets/navbar_icons/analytics.png",
                                                                className="navbar-icon",
                                                                alt="Analytics"
                                                            ),
                                                            href="/analytics",
                                                            className="navbar-nav-link",
                                                            title="Analytics"
                                                        ),
                                                        html.A(
                                                            html.Img(
                                                                src="/assets/navbar_icons/upload.png",
                                                                className="navbar-icon",
                                                                alt="Upload"
                                                            ),
                                                            href="/file-upload",
                                                            className="navbar-nav-link",
                                                            title="File Upload"
                                                        ),
                                                        html.A(
                                                            html.Img(
                                                                src="/assets/navbar_icons/print.png",
                                                                className="navbar-icon",
                                                                alt="Export"
                                                            ),
                                                            href="/export",
                                                            className="navbar-nav-link",
                                                            title="Export"
                                                        ),
                                                        html.A(
                                                            html.Img(
                                                                src="/assets/navbar_icons/setting.png",
                                                                className="navbar-icon",
                                                                alt="Settings"
                                                            ),
                                                            href="/settings",
                                                            className="navbar-nav-link",
                                                            title="Settings"
                                                        ),
                                                        html.A(
                                                            html.Img(
                                                                src="/assets/navbar_icons/logout.png",
                                                                className="navbar-icon",
                                                                alt="Logout"
                                                            ),
                                                            href="/logout",
                                                            className="navbar-nav-link",
                                                            title="Logout"
                                                        ),
                                                    ],
                                                    className="d-flex align-items-center",
                                                    style={"gap": "0.75rem"}
                                                ),

                                                # Language Toggle
                                                html.Div(
                                                    [
                                                        html.Span("EN", className="navbar-lang-active"),
                                                        html.Span(" | ", className="text-tertiary"),
                                                        html.Span("JP", className="navbar-lang-option"),
                                                    ],
                                                    className="ml-5 text-xs text-tertiary",
                                                    style={"cursor": "pointer"},
                                                    id="language-toggle"
                                                ),
                                            ],
                                            className="d-flex align-items-center justify-content-end",
                                        )
                                    ],
                                    width=3,
                                    className="d-flex align-items-center justify-content-end pr-4",
                                ),
                            ],
                            className="w-100 align-items-center",
                            style={"min-height": "60px"}
                        ),
                    ],
                    fluid=True,
                )
            ],
            color="primary",
            dark=True,
            sticky="top",
            className="navbar-main"
        )

    except Exception as e:
        print(f"Error creating navbar layout: {e}")
        return html.Div("Navbar unavailable", className="text-center text-danger p-3")


@safe_callback
def register_navbar_callbacks(app):
    """Register navbar callbacks for live updates"""
    if not DASH_AVAILABLE:
        return

    try:
        @app.callback(
            Output("live-time", "children"),
            Input("url-i18n", "pathname"),
        )
        def update_live_time(pathname):
            """Update live time display"""
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return f"Live: {current_time}"

        @app.callback(
            Output("language-toggle", "children"),
            Input("language-toggle", "n_clicks"),
            prevent_initial_call=True
        )
        def toggle_language(n_clicks):
            """Toggle between EN and JP languages"""
            if n_clicks and n_clicks % 2 == 1:
                return [
                    html.Span("EN", className="navbar-lang-option"),
                    html.Span(" | ", className="text-tertiary"),
                    html.Span("JP", className="navbar-lang-active"),
                ]
            else:
                return [
                    html.Span("EN", className="navbar-lang-active"),
                    html.Span(" | ", className="text-tertiary"),
                    html.Span("JP", className="navbar-lang-option"),
                ]

        @app.callback(
            Output("page-context", "children"),
            Input("url-i18n", "pathname"),
        )
        def update_page_context(pathname):
            """Update page context based on current route"""
            page_contexts = {
                "/": "Dashboard – Tokyo HQ",
                "/analytics": "Analytics – Data Intelligence",
                "/file-upload": "File Upload – Data Management",
                "/export": "Export – Report Generation",
                "/settings": "Settings – System Configuration",
                "/logout": "Logout – Session Management"
            }
            return page_contexts.get(pathname, "Tokyo HQ – East Wing")

    except Exception as e:
        print(f"Error registering navbar callbacks: {e}")


# Export functions for component registry
layout = create_navbar_layout
__all__ = ["create_navbar_layout", "register_navbar_callbacks", "layout"]
