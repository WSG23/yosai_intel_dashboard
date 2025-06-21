"""File Upload Page - Uses Plugin Architecture"""
from typing import Optional
import logging

# Safe imports with fallbacks
try:
    from dash import html, dcc, Input, Output, State, callback
    import dash_bootstrap_components as dbc
    DASH_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    DASH_AVAILABLE = False
    html = dcc = dbc = None

try:
    from plugins.file_upload_plugin import FileUploadPlugin
    PLUGIN_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    PLUGIN_AVAILABLE = False

logger = logging.getLogger(__name__)


def layout():
    """File Upload page layout using plugin"""
    if not DASH_AVAILABLE:
        return "File Upload page not available - Dash components missing"

    if not PLUGIN_AVAILABLE:
        return dbc.Container([
            dbc.Alert("File Upload Plugin not available", color="danger")
        ])

    # Use plugin directly
    plugin = FileUploadPlugin()

    return dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H1("\U0001F4C1 File Upload Manager", className="text-primary mb-0"),
                html.P("Upload and validate CSV, JSON, and Excel files", className="text-secondary mb-4"),
            ])
        ]),

        # Plugin component
        dbc.Row([
            dbc.Col([
                plugin.create_dual_file_uploader("file-upload-main")
            ])
        ], className="mb-4"),

        # Data storage
        dcc.Store(id="file-upload-data-store", data={}),

        # File management section
        dbc.Row([
            dbc.Col([
                html.Div(id="file-management-section", className="mt-4")
            ])
        ])
    ], fluid=True, className="p-4")


def register_file_upload_callbacks(app, container=None):
    """Register file upload page callbacks using plugin"""
    if not DASH_AVAILABLE or not PLUGIN_AVAILABLE:
        logger.warning("File upload callbacks not registered - components not available")
        return

    # Use plugin for callback registration
    plugin = FileUploadPlugin()
    plugin.register_callbacks(app, container)

    # Additional page-specific callbacks can go here
    @app.callback(
        Output("file-management-section", "children"),
        Input("file-upload-data-store", "data"),
        prevent_initial_call=True,
    )
    def update_file_management(data):
        if not data:
            return html.Div("No files uploaded yet")

        return dbc.Alert(f"Files uploaded: {len(data.get('files', []))}", color="info")


def _create_success_alert(message: str):
    """Create success alert"""
    return dbc.Alert(message, color="success", dismissable=True)


def _create_warning_alert(message: str):
    """Create warning alert"""
    return dbc.Alert(message, color="warning", dismissable=True)


def _create_error_alert(message: str):
    """Create error alert"""
    return dbc.Alert(message, color="danger", dismissable=True)


def _create_file_info_card(df, filename: str):
    """Create file info card"""
    return dbc.Card([
        dbc.CardHeader(f"File: {filename}"),
        dbc.CardBody([
            html.P(f"Rows: {len(df)}"),
            html.P(f"Columns: {len(df.columns)}"),
            html.P(f"Columns: {', '.join(df.columns.tolist())}")
        ])
    ])

__all__ = ["layout", "register_file_upload_callbacks"]
