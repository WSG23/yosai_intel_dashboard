"""File Upload Page - Direct component import"""
from typing import Optional, Union, List, Dict, Any, Tuple
import logging

# Safe imports with fallbacks
try:
    from dash import html, dcc, Input, Output, State, callback
    import dash_bootstrap_components as dbc
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    html = dcc = dbc = None

try:
    from components.analytics import (
        create_dual_file_uploader,
        register_dual_upload_callbacks,
        FileProcessor,
        UPLOAD_AVAILABLE,
    )
except ImportError:
    UPLOAD_AVAILABLE = False
    FileProcessor = None

logger = logging.getLogger(__name__)


def safe_text(text):
    """Return text safely, handling any objects"""
    if text is None:
        return ""
    return str(text)


def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def _create_success_alert(message: str):
    """Create success alert"""
    if not DASH_AVAILABLE:
        return f"SUCCESS: {message}"
    return dbc.Alert(message, color="success", dismissable=True)


def _create_warning_alert(message: str):
    """Create warning alert"""
    if not DASH_AVAILABLE:
        return f"WARNING: {message}"
    return dbc.Alert(message, color="warning", dismissable=True)


def _create_error_alert(message: str):
    """Create error alert"""
    if not DASH_AVAILABLE:
        return f"ERROR: {message}"
    return dbc.Alert(message, color="danger", dismissable=True)


def _create_file_info_card(df, filename: str):
    """Create file info card"""
    if not DASH_AVAILABLE:
        return f"File: {filename}, Rows: {len(df)}"

    return dbc.Card([
        dbc.CardHeader(f"\U0001F4C4 File: {filename}"),
        dbc.CardBody([
            html.P(f"\U0001F4CA Rows: {len(df):,}"),
            html.P(f"\U0001F4CB Columns: {len(df.columns)}"),
            html.P(f"\U0001F3F7\uFE0F Column Names: {', '.join(df.columns.tolist())}")
        ])
    ], className="mt-3")


def layout():
    """File Upload page layout using direct components"""
    if not DASH_AVAILABLE:
        return "File Upload page not available - Dash components missing"

    return dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H1(
                    "\U0001F4C1 File Upload Manager",
                    className="text-primary mb-0"
                ),
                html.P(
                    "Upload and validate CSV, JSON, and Excel files",
                    className="text-secondary mb-4",
                ),
            ])
        ]),

        # Debug info (remove after testing)
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.P(f"DASH_AVAILABLE: {DASH_AVAILABLE}"),
                    html.P(f"UPLOAD_AVAILABLE: {UPLOAD_AVAILABLE}"),
                    html.P(f"FileProcessor available: {FileProcessor is not None}")
                ], color="info", className="mb-3")
            ])
        ]),

        # File upload section
        dbc.Row([
            dbc.Col([
                create_dual_file_uploader("file-upload-main") if UPLOAD_AVAILABLE
                else _create_error_alert("File uploader not available")
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
    """Register file upload page callbacks using direct components"""
    if not DASH_AVAILABLE or not UPLOAD_AVAILABLE:
        logger.warning("File upload callbacks not registered - components not available")
        return

    # Register component callbacks
    register_dual_upload_callbacks(app, "file-upload-main")

    # Page-specific callback for file management
    @app.callback(
        Output("file-management-section", "children"),
        Input("file-upload-data-store", "data"),
        prevent_initial_call=True,
    )
    def update_file_management(data):
        if not data:
            return html.Div("No files uploaded yet", className="text-muted")

        files = data.get('files', [])
        return dbc.Alert(
            f"Files uploaded: {len(files)}", 
            color="info" if files else "secondary"
        )

    # File processing callback
    @app.callback(
        [
            Output("file-upload-main-status", "children"),
            Output("file-upload-data-store", "data"),
            Output("file-upload-main-info", "children"),
        ],
        Input("file-upload-main", "contents"),
        State("file-upload-main", "filename"),
        prevent_initial_call=True,
    )
    def process_file_uploads(
        contents_list: Optional[Union[str, List[str]]],
        filename_list: Optional[Union[str, List[str]]],
    ) -> Tuple[html.Div, Dict[str, Any], html.Div]:
        """Process uploaded files and provide detailed information"""

        if not contents_list:
            return (
                html.Div(),
                {},
                html.Div(),
            )

        if isinstance(contents_list, str):
            contents_list = [contents_list]
        if isinstance(filename_list, str):
            filename_list = [filename_list]

        try:
            upload_status = []
            file_info = []
            all_data = {"files": []}

            for i, (contents, filename) in enumerate(zip(contents_list, filename_list)):
                try:
                    if FileProcessor:
                        processed_data = FileProcessor.process_file_content(contents, filename)

                        # FIXED: Proper DataFrame validation
                        if processed_data is not None and not processed_data.empty:
                            upload_status.append(_create_success_alert(f"\u2705 {filename} uploaded successfully"))
                            file_info.append(_create_file_info_card(processed_data, filename))
                            all_data["files"].append(filename)
                        else:
                            upload_status.append(_create_error_alert(f"\u274C Failed to process {filename} - file may be empty or invalid"))
                    else:
                        upload_status.append(_create_warning_alert(f"\u26A0\uFE0F FileProcessor not available for {filename}"))

                except Exception as e:
                    upload_status.append(_create_error_alert(f"\u274C Error processing {filename}: {str(e)}"))

            return (
                html.Div(upload_status),
                all_data,
                html.Div(file_info),
            )

        except Exception as e:
            logger.error(f"File upload processing error: {e}")
            return (
                _create_error_alert(f"Processing error: {str(e)}"),
                {},
                html.Div(),
            )
