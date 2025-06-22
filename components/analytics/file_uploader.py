"""
Dual Upload Box Component with Tailwind styling
"""
from dash import html, dcc, clientside_callback, Input, Output, State, callback
import dash_bootstrap_components as dbc
import logging
import pandas as pd
import base64
import io
import dash

logger = logging.getLogger(__name__)


def create_dual_file_uploader(upload_id: str = 'analytics-file-upload') -> html.Div:
    """Create dual upload box interface"""
    try:
        return html.Div([
            # Header section
            html.Div([
                html.H3("\U0001F4C1 File Upload Manager", className="upload-section-title"),
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
                                src="/assets/navbar_icons/upload.png",
                                className="upload-icon",
                                id=f"{upload_id}-icon"
                            ),

                            # Title and subtitle
                            html.Div("File Upload", className="upload-box-title"),
                            html.Div("Drag & drop or click", className="upload-box-subtitle"),

                            # Supported file types
                            html.Div([
                                html.P("\u2705 CSV files (.csv)"),
                                html.P("\u2705 JSON files (.json)"),
                                html.P("\u2705 Excel files (.xlsx, .xls)")
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
                        html.P("\U0001F504 MySQL connections"),
                        html.P("\U0001F504 PostgreSQL support"),
                        html.P("\U0001F504 Cloud integrations")
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


def register_dual_upload_callbacks(app, upload_id: str = 'upload-data'):
    """Register callbacks for dual upload functionality"""
    try:
        app.clientside_callback(
            f"""
            function(contents, filename, current_state) {{
                if (!contents) {{
                    return [
                        '/assets/navbar_icons/upload.png',
                        'upload-box upload-box-active',
                        'upload-progress-overlay',
                        {{status: 'idle', files: []}}
                    ];
                }}
                return [
                    '/assets/navbar_icons/upload.png',
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
                "/assets/navbar_icons/upload.png",
                "upload-box upload-box-active",
                "upload-progress-overlay",
                "Ready for upload",
                "/assets/navbar_icons/upload.png"
            ]
    except Exception as e:
        logger.error(f"Error registering dual upload callbacks: {e}")

    @app.callback(
        [
            Output("door-mapping-modal-data-trigger", "data"),
            Output("door-mapping-modal-trigger", "n_clicks")
        ],
        [Input('upload-data', "contents")],
        [State('upload-data', "filename")],
        prevent_initial_call=True
    )
    def trigger_door_mapping_modal(contents, filename):
        """Trigger door mapping modal after successful file upload"""
        if contents is None:
            raise dash.exceptions.PreventUpdate

        try:
            from services.door_mapping_service import door_mapping_service

            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)

            if filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                df = pd.read_excel(io.BytesIO(decoded))
            elif filename.endswith('.json'):
                df = pd.read_json(io.StringIO(decoded.decode('utf-8')))
            else:
                raise ValueError("Unsupported file format")

            modal_data = door_mapping_service.process_uploaded_data(df)

            return modal_data, 1

        except Exception as e:
            logger.error(f"Error processing file for door mapping: {e}")
            raise dash.exceptions.PreventUpdate

layout = create_dual_file_uploader
__all__ = [
    "create_dual_file_uploader",
    "register_dual_upload_callbacks",
    "layout",
    "render_column_mapping_panel",
    "handle_door_mapping"
]


def render_column_mapping_panel(header_options, file_name="access_control_data_1.csv",
                               ai_suggestions=None, floor_estimate=None, user_id="default"):
    """Enhanced column mapping UI panel with AI suggestions and verification."""

    # Get AI suggestions from your existing plugin
    if ai_suggestions is None and header_options:
        try:
            from plugins.ai_classification.plugin import AIClassificationPlugin
            from plugins.ai_classification.config import get_ai_config

            ai_plugin = AIClassificationPlugin(get_ai_config())
            ai_plugin.start()

            mapping_result = ai_plugin.map_columns(header_options, user_id)

            if mapping_result and mapping_result.get('success'):
                ai_suggestions = mapping_result.get('suggested_mapping', {})

                # Use your existing floor estimation (simplified for headers only)
                floor_result = {'total_floors': 3, 'confidence': 0.5}  # Default
                floor_estimate = floor_result

        except Exception as e:
            logger.warning(f"AI plugin not available: {e}")
            ai_suggestions = {}
            floor_estimate = {'total_floors': 1, 'confidence': 0.0}

    # Map AI suggestions to required fields (priority order)
    timestamp_value = ""
    device_value = ""
    user_value = ""
    result_value = ""

    if ai_suggestions:
        for csv_col, std_field in ai_suggestions.items():
            if std_field == 'timestamp':
                timestamp_value = csv_col
            elif std_field in ['location', 'device_id', 'door']:
                device_value = csv_col
            elif std_field in ['user_id', 'token_id', 'badge_id']:
                user_value = csv_col
            elif std_field in ['access_type', 'access_result', 'event_type']:
                result_value = csv_col

    estimated_floors = floor_estimate.get('total_floors', 1) if floor_estimate else 1

    def column_dropdown(label, required=False, field_id=None, suggested_value=None):
        return html.Div(className="form-field", children=[
            html.Label(label, className="form-label" + (" form-label--required" if required else "")),
            dcc.Dropdown(
                id=field_id,
                options=[{"label": col, "value": col} for col in header_options],
                value=suggested_value,
                placeholder="Select a column...",
                className="form-select"
            )
        ])

    return html.Div(className="modal-overlay", children=[
        html.Div(className="modal modal--xl", children=[
            html.Div(className="modal__header", children=[
                html.H2("Verify AI Mapping", className="modal__title"),
                html.Button("×", id="close-mapping-modal", className="modal__close")
            ]),

            html.Div(className="modal__body", children=[
                # File Information
                html.Div(className="form-row", children=[
                    html.Div(className="form-field", children=[
                        html.Label("File", className="form-label form-label--required"),
                        html.Div(file_name, className="form-input form-input--readonly")
                    ]),
                    html.Div(className="form-field", children=[
                        html.Label("Timestamp", className="form-label form-label--required"),
                        html.Div("Timestamp", className="form-input form-input--readonly")
                    ]),
                    html.Div(className="form-field", children=[
                        html.Label("Device ID", className="form-label"),
                        html.Div("Door", className="form-input form-input--readonly")
                    ])
                ]),

                html.Hr(className="form-separator"),

                # Instructions
                html.Div(className="form-instructions", children=[
                    html.P("Select the column containing the device ID or another identifier",
                           className="form-instructions-text")
                ]),

                # Main Column Mapping - Priority Order
                html.Div(className="form-section", children=[
                    html.H3("Column Mapping", className="form-section-title"),

                    # Priority 1: Timestamp (Required)
                    column_dropdown("Timestamp", required=True, field_id="timestamp-dropdown",
                                  suggested_value=timestamp_value),

                    # Priority 2: Door/Location (Device Name)
                    column_dropdown("Door Name", required=False, field_id="device-column-dropdown",
                                  suggested_value=device_value),

                    # Priority 3: Token ID (User ID)
                    column_dropdown("User ID", required=False, field_id="user-id",
                                  suggested_value=user_value),

                    # Priority 4: Access Result (Event Type)
                    column_dropdown("Event Type", required=False, field_id="event-type-dropdown",
                                  suggested_value=result_value),
                ]),

                html.Hr(className="form-separator"),

                # AI Floor Estimation Section
                html.Div(className="form-section", children=[
                    html.H3("AI Floor Estimation", className="form-section-title"),
                    html.Div(className="form-field", children=[
                        html.Label("Estimated Floors (AI Generated - Adjustable)", className="form-label"),
                        dcc.Input(
                            id="floor-estimate-input",
                            type="number",
                            value=estimated_floors,
                            min=1,
                            max=100,
                            className="form-input",
                            style={"width": "100px"}
                        ),
                        html.Small(f"AI Confidence: {floor_estimate.get('confidence', 0) * 100:.0f}%" if floor_estimate else "AI Confidence: 0%",
                                 className="form-help-text")
                    ])
                ]),

                # Hidden storage for user ID
                html.Div(id="user-id-storage", children=user_id, style={"display": "none"})
            ]),

            html.Div(className="modal__footer", children=[
                html.Button("Cancel", id="cancel-mapping", className="form-input"),
                html.Button("Verify & Learn", id="verify-mapping", className="form-input", style={
                    "backgroundColor": "var(--color-accent)",
                    "color": "white",
                    "fontWeight": "bold"
                })
            ])
        ])
    ])


@callback(
    [Output('door-mapping-modal', 'children'),
     Output('door-mapping-modal', 'style')],
    [Input('open-door-mapping', 'n_clicks'),
     Input('skip-door-mapping', 'n_clicks')],
    prevent_initial_call=True
)
def handle_door_mapping(open_clicks, skip_clicks):
    """Handle door mapping modal"""
    if skip_clicks:
        return [], {'display': 'none'}

    if open_clicks:
        try:
            from components.door_mapping_modal import create_door_mapping_modal

            modal_content = create_door_mapping_modal()
            return modal_content, {'display': 'block'}

        except ImportError:
            return html.Div("Door mapping modal not found"), {'display': 'block'}

    return [], {'display': 'none'}

