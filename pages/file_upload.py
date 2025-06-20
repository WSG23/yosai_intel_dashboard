"""
File Upload Page - Separated from Deep Analytics
Handles CSV, JSON, and Excel file uploads with validation
"""
from typing import Optional, Union, List, Dict, Any, Tuple
import logging

# Define safe_text directly to avoid import issues
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

# Safe imports with fallbacks
try:
    from dash import html, dcc, Input, Output, State, callback
    import dash_bootstrap_components as dbc
    DASH_AVAILABLE = True
except ImportError:
    DASH_AVAILABLE = False
    html = dcc = dbc = None

try:
    from components.analytics.file_uploader import create_file_uploader
    from components.analytics.file_processing import FileProcessor
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    FileProcessor = None

logger = logging.getLogger(__name__)


def layout():
    """File Upload page layout"""
    if not DASH_AVAILABLE:
        return "File Upload page not available - Dash components missing"

    return dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H1(
                    safe_text("\U0001F4C1 File Upload Manager"),
                    className="text-primary mb-0"
                ),
                html.P(
                    safe_text("Upload and validate CSV, JSON, and Excel files"),
                    className="text-secondary mb-4",
                ),
            ])
        ]),

        # File upload section
        dbc.Row([
            dbc.Col([
                create_file_uploader("file-upload-main") if COMPONENTS_AVAILABLE
                else html.Div("File uploader not available")
            ])
        ]),

        # Upload status and file info
        dbc.Row([
            dbc.Col([
                html.Div(id="file-upload-status", className="mt-3"),
                html.Div(id="file-upload-info", className="mt-3"),
            ])
        ]),

        # Data storage for uploaded files
        dcc.Store(id="file-upload-data-store", data={}),

        # File management section
        dbc.Row([
            dbc.Col([
                html.Div(id="file-management-section", className="mt-4")
            ])
        ])
    ], fluid=True, className="p-4")


def register_file_upload_callbacks(app, container=None):
    """Register file upload page callbacks"""
    if not DASH_AVAILABLE or not COMPONENTS_AVAILABLE:
        logger.warning("File upload callbacks not registered - components not available")
        return

    @app.callback(
        [
            Output("file-upload-status", "children"),
            Output("file-upload-data-store", "data"),
            Output("file-upload-info", "children"),
            Output("file-management-section", "children"),
        ],
        Input("file-upload-main", "contents"),
        State("file-upload-main", "filename"),
        prevent_initial_call=True,
    )
    def process_file_uploads(
        contents_list: Optional[Union[str, List[str]]],
        filename_list: Optional[Union[str, List[str]]],
    ) -> Tuple[html.Div, Dict[str, Any], html.Div, html.Div]:
        """Process uploaded files and provide detailed information"""

        if not contents_list:
            return (
                html.Div(),
                {},
                html.Div(),
                html.Div(),
            )

        # Ensure inputs are lists
        if isinstance(contents_list, str):
            contents_list = [contents_list]
        if isinstance(filename_list, str):
            filename_list = [filename_list]

        upload_status = []
        file_info = []
        all_data = []
        management_components = []

        # Process each uploaded file
        for i, (contents, filename) in enumerate(zip(contents_list, filename_list)):
            try:
                # Process file content
                processed_data = FileProcessor.process_file_content(contents, filename)

                if processed_data is not None:
                    # Validate the dataframe
                    is_valid, message, suggestions = FileProcessor.validate_dataframe(
                        processed_data
                    )

                    if is_valid:
                        file_id = f"file_{i}_{filename}"

                        # Success status
                        upload_status.append(_create_success_alert(
                            f"\u2705 {filename} uploaded successfully ({len(processed_data)} rows, {len(processed_data.columns)} columns)"
                        ))

                        # Detailed file info
                        file_info.append(_create_file_info_card(processed_data, filename))

                        # Store data
                        all_data.append({
                            "id": file_id,
                            "filename": filename,
                            "data": processed_data.to_dict("records"),
                            "shape": processed_data.shape,
                            "columns": list(processed_data.columns),
                            "dtypes": processed_data.dtypes.to_dict(),
                        })

                        # Management components
                        management_components.append(_create_file_management_card(
                            file_id, filename, processed_data
                        ))

                    else:
                        upload_status.append(_create_warning_alert(
                            f"\u26A0\uFE0F {filename}: {message}"
                        ))
                        if suggestions:
                            upload_status.append(_create_info_alert(
                                f"\U0001F4A1 Suggestions: {', '.join(suggestions)}"
                            ))
                else:
                    upload_status.append(_create_error_alert(
                        f"\u274C Failed to process {filename}"
                    ))

            except Exception as e:
                upload_status.append(_create_error_alert(
                    f"\u274C Error processing {filename}: {str(e)}"
                ))

        return (
            html.Div(upload_status),
            {"files": all_data},
            html.Div(file_info),
            html.Div(management_components) if management_components else html.Div()
        )


def _create_success_alert(message: str) -> dbc.Alert:
    """Create a success alert message"""
    return dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"), safe_text(message)],
        color="success",
        className="mb-2",
    )


def _create_warning_alert(message: str) -> dbc.Alert:
    """Create a warning alert message"""
    return dbc.Alert(
        [html.I(className="fas fa-exclamation-triangle me-2"), safe_text(message)],
        color="warning",
        className="mb-2",
    )


def _create_error_alert(message: str) -> dbc.Alert:
    """Create an error alert message"""
    return dbc.Alert(
        [html.I(className="fas fa-times-circle me-2"), safe_text(message)],
        color="danger",
        className="mb-2",
    )


def _create_info_alert(message: str) -> dbc.Alert:
    """Create an info alert message"""
    return dbc.Alert(
        [html.I(className="fas fa-info-circle me-2"), safe_text(message)],
        color="info",
        className="mb-2",
    )


def _create_file_info_card(df, filename: str) -> dbc.Card:
    """Create detailed file information card"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5(f"\U0001F4CA {safe_text(filename)}", className="mb-0"),
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.P(f"Rows: {len(df)}", className="mb-1"),
                    html.P(f"Columns: {len(df.columns)}", className="mb-1"),
                ], width=6),
                dbc.Col([
                    html.P(f"Memory: {format_file_size(df.memory_usage(deep=True).sum())}", className="mb-1"),
                    html.P(f"Null values: {df.isnull().sum().sum()}", className="mb-1"),
                ], width=6),
            ]),
            html.Hr(),
            html.H6("Column Types:", className="mt-2"),
            html.Div([
                dbc.Badge(f"{safe_text(col)}: {safe_text(dtype)}", color="secondary", className="me-1 mb-1")
                for col, dtype in df.dtypes.items()
            ]),
        ])
    ], className="mb-3")


def _create_file_management_card(file_id: str, filename: str, df) -> dbc.Card:
    """Create file management card with actions"""
    return dbc.Card([
        dbc.CardHeader([
            html.H6(f"\U0001F527 Manage {safe_text(filename)}", className="mb-0"),
        ]),
        dbc.CardBody([
            dbc.ButtonGroup([
                dbc.Button("Preview Data", id=f"preview-{file_id}", color="primary", size="sm"),
                dbc.Button("Export Analytics", id=f"export-{file_id}", color="success", size="sm"),
                dbc.Button("Remove File", id=f"remove-{file_id}", color="danger", size="sm"),
            ], className="mb-2"),
            html.Div(id=f"file-actions-{file_id}")
        ])
    ], className="mb-3")


__all__ = ["layout", "register_file_upload_callbacks"]
