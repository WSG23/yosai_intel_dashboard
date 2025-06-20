"""
Dual Upload Box Component with Tailwind styling
"""
from dash import html, dcc, clientside_callback, Input, Output, State
import dash_bootstrap_components as dbc
import logging

logger = logging.getLogger(__name__)


def create_dual_file_uploader(upload_id: str = 'analytics-file-upload') -> html.Div:
    """Create dual upload box interface"""
    try:
        return html.Div([
            # Header section
            html.Div([
                html.H3("📁 File Upload Manager", className="upload-section-title"),
                html.P("Upload and validate CSV, JSON, and Excel files", className="upload-section-subtitle")
            ], className="text-center mb-4"),

            # Dual upload container
            html.Div([
                # Left Box - Active File Upload
                html.Div([
                    dcc.Upload(
                        id=upload_id,
                        children=html.Div([
                            # Upload icon (will be dynamically updated)
                            html.Img(
                                src="/assets/upload_file_csv_icon.png",
                                className="upload-icon",
                                id=f"{upload_id}-icon"
                            ),

                            # Title and subtitle
                            html.Div("File Upload", className="upload-box-title"),
                            html.Div("Drag & drop or click", className="upload-box-subtitle"),

                            # Supported file types
                            html.Div([
                                html.P("✅ CSV files (.csv)"),
                                html.P("✅ JSON files (.json)"),
                                html.P("✅ Excel files (.xlsx, .xls)")
                            ], className="upload-supported-types")
                        ]),
                        multiple=True,
                        accept='.csv,.json,.xlsx,.xls,application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv'
                    ),

                    # Progress overlay
                    html.Div([
                        html.Div(className="upload-spinner"),
                        html.Div("Processing file...", id=f"{upload_id}-progress-text")
                    ], className="upload-progress-overlay", id=f"{upload_id}-progress")
                ],
                id=f"{upload_id}-box",
                className="upload-box upload-box-active",
                style={"position": "relative"}),

                # Right Box - Database Upload Placeholder
                html.Div([
                    html.Div("Coming Soon", className="upload-tooltip"),
                    html.Img(
                        src="/assets/navbar_icons/upload.png",
                        className="upload-icon",
                        id="database-upload-icon"
                    ),
                    html.Div("Database Upload", className="upload-box-title"),
                    html.Div("Connect to database", className="upload-box-subtitle"),
                    html.Div([
                        html.P("🔄 MySQL connections"),
                        html.P("🔄 PostgreSQL support"),
                        html.P("🔄 Cloud integrations")
                    ], className="upload-supported-types", style={"color": "var(--color-text-tertiary)"})
                ], className="upload-box upload-box-inactive", id="database-upload-box")

            ], className="dual-upload-container"),

            # Status and results area
            html.Div(id=f"{upload_id}-status", className="mt-4"),
            html.Div(id=f"{upload_id}-info", className="mt-3"),

            # Store for upload state
            dcc.Store(id=f"{upload_id}-state", data={"status": "idle", "files": []})

        ], className="dual-upload-wrapper")

    except Exception as e:
        logger.error(f"Error creating dual file uploader: {e}")
        return html.Div(f"Upload component error: {e}", className="text-danger")


def register_dual_upload_callbacks(app, upload_id: str = 'analytics-file-upload'):
    """Register callbacks for dual upload functionality"""
    try:
        app.clientside_callback(
            f"""
            function(contents, filename, current_state) {{
                if (!contents) {{
                    return [
                        '/assets/upload_file_csv_icon.png',
                        'upload-box upload-box-active',
                        'upload-progress-overlay',
                        {{status: 'idle', files: []}}
                    ];
                }}
                return [
                    '/assets/upload_file_csv_icon.png',
                    'upload-box upload-box-active',
                    'upload-progress-overlay show',
                    {{status: 'uploading', files: filename}}
                ];
            }}
            """,
            [
                Output(f"{upload_id}-icon", "src"),
                Output(f"{upload_id}-box", "className"),
                Output(f"{upload_id}-progress", "className"),
                Output(f"{upload_id}-state", "data")
            ],
            [
                Input(upload_id, "contents"),
                Input(upload_id, "filename"),
                State(f"{upload_id}-state", "data")
            ]
        )

        @app.callback(
            [
                Output(f"{upload_id}-icon", "src", allow_duplicate=True),
                Output(f"{upload_id}-box", "className", allow_duplicate=True),
                Output(f"{upload_id}-progress", "className", allow_duplicate=True),
                Output(f"{upload_id}-progress-text", "children"),
                Output("database-upload-icon", "src"),
            ],
            [
                Input(f"{upload_id}-status", "children"),
                State(f"{upload_id}-state", "data")
            ],
            prevent_initial_call=True
        )
        def update_upload_feedback(status_children, current_state):
            if status_children:
                status_str = str(status_children).lower()
                if "error" in status_str or "failed" in status_str:
                    return [
                        "/assets/upload_file_csv_icon_fail.png",
                        "upload-box upload-box-error",
                        "upload-progress-overlay",
                        "Upload failed",
                        "/assets/upload_file_csv_icon_fail.png"
                    ]
                elif "success" in status_str or "uploaded" in status_str:
                    return [
                        "/assets/upload_file_csv_icon_fail.png",
                        "upload-box upload-box-success",
                        "upload-progress-overlay",
                        "Upload complete",
                        "/assets/navbar_icons/upload.png"
                    ]
            return [
                "/assets/upload_file_csv_icon.png",
                "upload-box upload-box-active",
                "upload-progress-overlay",
                "Ready for upload",
                "/assets/navbar_icons/upload.png"
            ]
    except Exception as e:
        logger.error(f"Error registering dual upload callbacks: {e}")

layout = create_dual_file_uploader
__all__ = ["create_dual_file_uploader", "register_dual_upload_callbacks", "layout"]

