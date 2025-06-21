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


def register_dual_upload_callbacks(app, upload_id: str = 'analytics-file-upload'):
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
        [Input("analytics-file-upload", "contents")],
        [State("analytics-file-upload", "filename")],
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
    "verify_and_learn",
    "handle_door_mapping",
]


def render_column_mapping_panel(header_options, file_name="access_control_data_1.csv",
                               ai_suggestions=None, floor_estimate=None, user_id="default"):
    """Enhanced column mapping UI panel with AI suggestions and verification."""

    # Get AI suggestions from your existing plugin
    if ai_suggestions is None and header_options:
        try:
            # Import your existing AI plugin
            from plugins.ai_classification.plugin import AIClassificationPlugin
            from plugins.ai_classification.config import get_ai_config

            # Use your existing plugin
            ai_plugin = AIClassificationPlugin(get_ai_config())
            ai_plugin.start()

            # Use your existing column mapping service
            mapping_result = ai_plugin.map_columns(header_options, user_id)

            if mapping_result and mapping_result.get('success'):
                ai_suggestions = mapping_result.get('suggested_mapping', {})

                # Use your existing floor estimation (simplified for headers only)
                floor_result = {'total_floors': 3, 'confidence': 0.5}  # Default
                floor_estimate = floor_result

        except Exception as e:
            # Fallback if AI plugin not available
            logger.warning(f"AI plugin not available: {e}")
            ai_suggestions = {}
            floor_estimate = {'total_floors': 1, 'confidence': 0.0}

    # Map AI suggestions to your 4 required fields
    timestamp_value = ""
    device_value = "Door"  # Your default
    user_value = ""
    result_value = ""

    if ai_suggestions:
        # Map from AI suggestions to your required fields
        for csv_col, std_field in ai_suggestions.items():
            if std_field == 'timestamp':
                timestamp_value = csv_col
            elif std_field == 'location':
                device_value = csv_col
            elif std_field == 'user_id':
                user_value = csv_col
            elif std_field == 'access_type':
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

                html.Div(className="form-group", style={
                    "backgroundColor": "#f8f9fa",
                    "padding": "1rem",
                    "borderRadius": "8px",
                    "marginBottom": "1rem",
                    "borderLeft": "4px solid #007bff"
                }, children=[
                    html.H4("🤖 AI Detected:", style={"marginBottom": "0.5rem"}),
                    html.Div([
                        html.Div(f"✓ Timestamp → {timestamp_value}" if timestamp_value else "✗ Timestamp → Please select",
                               style={"color": "#28a745" if timestamp_value else "#dc3545"}),
                        html.Div(f"✓ Device/Door → {device_value}",
                               style={"color": "#28a745"}),
                        html.Div(f"✓ User ID → {user_value}" if user_value else "✗ User ID → Please select",
                               style={"color": "#28a745" if user_value else "#dc3545"}),
                        html.Div(f"✓ Access Result → {result_value}" if result_value else "✗ Access Result → Please select",
                               style={"color": "#28a745" if result_value else "#dc3545"}),
                    ]),
                    html.Small("Adjust dropdowns below if needed, then Verify to learn your preferences.")
                ]),

                html.Div(className="form-group", style={
                    "backgroundColor": "#e8f4fd",
                    "padding": "1rem",
                    "borderRadius": "8px",
                    "marginBottom": "1rem",
                    "borderLeft": "4px solid #17a2b8"
                }, children=[
                    html.H4("🏢 Floors:", style={"marginBottom": "0.5rem"}),
                    html.Div(style={"display": "flex", "alignItems": "center", "gap": "1rem"}, children=[
                        dcc.Input(
                            id="floor-count-input",
                            type="number",
                            value=estimated_floors,
                            min=1,
                            max=200,
                            style={"width": "80px", "padding": "0.25rem"}
                        ),
                        html.Span("floors")
                    ])
                ]),

                html.Hr(),

                html.Div(className="form-group", children=[
                    html.Div(className="form-field", children=[
                        html.Label("File", className="form-label form-label--required"),
                        html.Div(file_name, className="form-input")
                    ]),
                    html.Div(className="form-field", children=[
                        html.Label("Timestamp", className="form-label form-label--required"),
                        dcc.Dropdown(
                            id="timestamp-dropdown",
                            options=[{"label": col, "value": col} for col in header_options],
                            value=timestamp_value,
                            placeholder="Select timestamp column...",
                            className="form-select"
                        )
                    ]),
                    html.Div(className="form-field", children=[
                        html.Label("Device ID", className="form-label form-label--required"),
                        html.Div("Door", className="form-input")
                    ])
                ]),

                html.Hr(),

                html.Div([
                    html.Label("Select the column containing the device ID or another identifier", className="form-label"),
                    dcc.Dropdown(
                        id="device-column-dropdown",
                        options=[{"label": col, "value": col} for col in header_options],
                        placeholder="Select column for device ID",
                        className="form-select",
                        value=device_value
                    ),
                    html.Div(className="form-field", children=[
                        dcc.Checklist(
                            options=[{"label": "Separate device name", "value": "separate_device"}],
                            id="separate-device-toggle",
                            className="form-checkbox"
                        )
                    ])
                ], style={"marginTop": "2rem"}),

                html.Hr(),

                html.Div(className="form-group", children=[
                    html.Div(style={"flex": 1}, children=[
                        html.H4("Optional Columns", className="form-label"),
                        column_dropdown("Token ID", field_id="token-id", suggested_value=user_value),
                        column_dropdown("User ID", field_id="user-id", suggested_value=user_value),
                        column_dropdown("Entry/Exit", field_id="entry-exit", suggested_value=result_value),
                    ]),
                    html.Div(style={"flex": 1}, children=[
                        html.Div(style={"height": "2.5rem"}),
                        column_dropdown("Event Type", field_id="event-type", suggested_value=result_value),
                        column_dropdown("Door Name", field_id="door-name", suggested_value=device_value),
                        column_dropdown("Floor Number", field_id="floor-number"),
                    ])
                ]),

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
    Output('mapping-verified-status', 'children'),
    Input('verify-mapping', 'n_clicks'),
    [State('timestamp-dropdown', 'value'),
     State('device-column-dropdown', 'value'),
     State('user-id', 'value'),
     State('entry-exit', 'value'),
     State('floor-count-input', 'value'),
     State('user-id-storage', 'children')],
    prevent_initial_call=True
)
def verify_and_learn(n_clicks, timestamp_col, device_col, user_col, result_col, floor_count, user_id):
    """Use your existing AI plugin to learn from verification"""
    if not n_clicks:
        return ""

    try:
        from plugins.ai_classification.plugin import AIClassificationPlugin

        ai_plugin = AIClassificationPlugin()
        ai_plugin.start()

        user_mapping = {
            'timestamp': timestamp_col,
            'device_id': device_col,
            'user_id': user_col,
            'access_result': result_col
        }

        ai_plugin.record_correction(
            device_name=device_col,
            ai_prediction={'suggested_mapping': user_mapping},
            user_correction={'confirmed_mapping': user_mapping, 'floors': floor_count},
            client_id=user_id
        )

        return html.Div([
            html.Div("✅ Mapping verified and learned!", className="alert alert-success"),
            html.Small(f"Your preferences saved for future uploads. Floors: {floor_count}"),
            html.Div(style={"marginTop": "1rem", "padding": "1rem", "backgroundColor": "#f8f9fa", "borderRadius": "4px"}, children=[
                html.P("Would you like to manually adjust door settings?", style={"marginBottom": "0.5rem"}),
                html.Button("Yes, Adjust Doors", id="open-door-mapping", className="btn btn-primary", style={"marginRight": "0.5rem"}),
                html.Button("No, Continue", id="skip-door-mapping", className="btn btn-secondary")
            ])
        ])

    except Exception as e:
        return html.Div([
            html.Div("❌ Error saving mapping", className="alert alert-danger"),
            html.Small(str(e))
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
            from door_mapping_modal import render_door_mapping_modal

            modal_content = render_door_mapping_modal()
            return modal_content, {'display': 'block'}

        except ImportError:
            return html.Div("Door mapping modal not found"), {'display': 'block'}

    return [], {'display': 'none'}

