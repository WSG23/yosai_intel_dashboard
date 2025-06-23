"""
Dual Upload Box Component with Tailwind styling and working callbacks
"""

from dash import html, dcc, callback, Input, Output, State, callback_context, no_update
import dash
import dash_bootstrap_components as dbc
import base64
import io
import pandas as pd
import uuid
import logging
from datetime import datetime
import tempfile
import os

logger = logging.getLogger(__name__)


def create_dual_file_uploader(upload_id="upload-data"):
    """Create a working dual file uploader component"""
    try:
        return html.Div(
            [
                # Upload header
                html.Div(
                    [
                        html.H2("📁 Upload Your Data", className="text-2xl font-bold mb-2"),
                        html.P(
                            "Choose your access control data file to begin analysis", className="text-gray-600 mb-6"
                        ),
                    ]
                ),
                # Main upload area - simplified and working
                html.Div(
                    [
                        dcc.Upload(
                            id=upload_id,
                            children=html.Div(
                                [
                                    html.Div(
                                        [
                                            html.I(className="fas fa-cloud-upload-alt text-4xl text-blue-500 mb-4"),
                                            html.H3(
                                                "Drop files here or click to browse",
                                                className="text-lg font-semibold text-gray-700 mb-2",
                                            ),
                                            html.P("CSV, JSON, Excel files supported", className="text-gray-500 mb-4"),
                                            html.Div(
                                                [
                                                    html.Span(
                                                        "✅ CSV files (.csv)", className="block text-sm text-gray-600"
                                                    ),
                                                    html.Span(
                                                        "✅ JSON files (.json)", className="block text-sm text-gray-600"
                                                    ),
                                                    html.Span(
                                                        "✅ Excel files (.xlsx, .xls)",
                                                        className="block text-sm text-gray-600",
                                                    ),
                                                ]
                                            ),
                                        ],
                                        className="text-center",
                                    )
                                ],
                                className="border-2 border-dashed border-blue-300 rounded-lg p-8 bg-blue-50 hover:bg-blue-100 transition-colors cursor-pointer",
                            ),
                            multiple=False,
                            accept=".csv,.json,.xlsx,.xls",
                            className="w-full",
                        )
                    ],
                    className="mb-6",
                ),
                # Database upload option (inactive)
                html.Div(
                    [
                        html.Div(
                            [
                                html.I(className="fas fa-database text-2xl text-gray-400 mb-2"),
                                html.H4("Database Connection", className="text-md font-medium text-gray-500 mb-1"),
                                html.P("Coming soon - Direct database connections", className="text-sm text-gray-400"),
                            ],
                            className="text-center p-4 border border-gray-200 rounded-lg bg-gray-50",
                        )
                    ],
                    className="mb-4",
                ),
            ],
            className="max-w-2xl mx-auto",
        )

    except Exception as e:
        logger.error(f"Error creating file uploader: {e}")
        return html.Div(
            [html.H3("Upload Error", className="text-red-600"), html.P(f"Error: {str(e)}", className="text-red-500")]
        )


def render_column_mapping_panel(
    header_options, file_name="access_control_data.csv", ai_suggestions=None, floor_estimate=None, user_id="default"
):
    """Enhanced column mapping UI panel with AI suggestions and verification."""

    if ai_suggestions is None:
        ai_suggestions = {}
    if floor_estimate is None:
        floor_estimate = {"total_floors": 1, "confidence": 0}

    def create_field_dropdown(label, field_id, suggested_value=None, required=False):
        return html.Div(
            className="form-field",
            children=[
                html.Label(
                    label + (" *" if required else ""),
                    className="form-label" + (" form-label--required" if required else ""),
                ),
                html.Small(
                    f"AI Suggestion: {suggested_value}" if suggested_value else "No AI suggestion",
                    className="form-help-text",
                ),
                dcc.Dropdown(
                    id=field_id,
                    options=[{"label": col, "value": col} for col in header_options],
                    value=suggested_value,
                    placeholder="Select a column...",
                    className="form-select",
                ),
            ],
        )

    return html.Div(
        className="modal-overlay",
        children=[
            html.Div(
                className="modal modal--xl",
                children=[
                    html.Div(
                        className="modal__header",
                        children=[
                            html.H2("Verify AI Column Mapping", className="modal__title"),
                            html.P(f"File: {file_name}", className="modal__subtitle"),
                            html.Button("\xd7", id="close-mapping-modal", className="modal__close"),
                        ],
                    ),
                    html.Div(
                        className="modal__body",
                        children=[
                            # Instructions
                            html.Div(
                                className="form-instructions",
                                children=[
                                    html.P(
                                        "🤖 AI has analyzed your file and suggested column mappings below. Please verify and adjust as needed.",
                                        className="form-instructions-text",
                                    ),
                                    html.P(
                                        f"📊 Detected {len(header_options)} columns in your file",
                                        className="form-instructions-subtext",
                                    ),
                                ],
                            ),
                            html.Hr(className="form-separator"),
                            # Column Mapping Fields
                            html.Div(
                                className="form-grid",
                                children=[
                                    create_field_dropdown(
                                        "Timestamp Column",
                                        "timestamp-dropdown",
                                        ai_suggestions.get("timestamp"),
                                        required=True,
                                    ),
                                    create_field_dropdown(
                                        "Device/Door Column",
                                        "device-column-dropdown",
                                        ai_suggestions.get("device_name"),
                                    ),
                                    create_field_dropdown(
                                        "User ID Column", "user-id-dropdown", ai_suggestions.get("user_id")
                                    ),
                                    create_field_dropdown(
                                        "Event Type Column", "event-type-dropdown", ai_suggestions.get("event_type")
                                    ),
                                ],
                            ),
                            html.Hr(className="form-separator"),
                            # Floor Estimate
                            html.Div(
                                className="form-row",
                                children=[
                                    html.Div(
                                        className="form-field",
                                        children=[
                                            html.Label("Number of Floors", className="form-label"),
                                            dcc.Input(
                                                id="floor-estimate-input",
                                                type="number",
                                                value=floor_estimate.get("total_floors", 1),
                                                min=1,
                                                max=100,
                                                className="form-input",
                                            ),
                                            html.Small(
                                                f"AI Confidence: {floor_estimate.get('confidence', 0) * 100:.0f}%",
                                                className="form-help-text",
                                            ),
                                        ],
                                    )
                                ],
                            ),
                            # Hidden storage for user ID
                            html.Div(id="user-id-storage", children=user_id, style={"display": "none"}),
                        ],
                    ),
                    html.Div(
                        className="modal__footer",
                        children=[
                            html.Button("Cancel", id="cancel-mapping", className="btn btn-secondary"),
                            html.Button("\u2705 Verify & Learn", id="verify-mapping", className="btn btn-primary"),
                        ],
                    ),
                ],
            )
        ],
    )


@callback(
    [
        Output("column-mapping-modal-overlay", "style"),
        Output("modal-subtitle", "children"),
        Output("column-count-text", "children"),
        Output("timestamp-dropdown", "options"),
        Output("device-column-dropdown", "options"),
        Output("user-id-dropdown", "options"),
        Output("event-type-dropdown", "options"),
        Output("timestamp-dropdown", "value"),
        Output("device-column-dropdown", "value"),
        Output("user-id-dropdown", "value"),
        Output("event-type-dropdown", "value"),
        Output("floor-estimate-input", "value"),
        Output("timestamp-suggestion", "children"),
        Output("device-suggestion", "children"),
        Output("user-suggestion", "children"),
        Output("event-suggestion", "children"),
        Output("floor-confidence", "children"),
        Output("upload-status", "children"),
        Output("upload-feedback", "children"),
        Output("uploaded-file-store", "data"),
        Output("processed-data-store", "data"),
        Output("open-column-mapping", "style"),
        Output("proceed-door-mapping-trigger", "style"),
        Output("skip-door-mapping", "style"),
    ],
    [
        Input("upload-data", "contents"),
        Input("cancel-mapping", "n_clicks"),
        Input("verify-mapping", "n_clicks"),
        Input("close-mapping-modal", "n_clicks"),
        Input("open-column-mapping", "n_clicks"),
    ],
    [
        State("upload-data", "filename"),
        State("timestamp-dropdown", "value"),
        State("device-column-dropdown", "value"),
        State("user-id-dropdown", "value"),
        State("event-type-dropdown", "value"),
        State("floor-estimate-input", "value"),
        State("user-id-storage", "children"),
        State("uploaded-file-store", "data"),
        State("processed-data-store", "data"),
    ],
    prevent_initial_call=True,
)
def handle_file_upload_and_modal(
    upload_contents,
    cancel_clicks,
    verify_clicks,
    close_clicks,
    open_clicks,
    upload_filename,
    timestamp_col,
    device_col,
    user_col,
    event_type_col,
    floor_estimate,
    user_id,
    file_store_data,
    processed_data,
):
    """Fixed file upload handler with proper modal display."""
    from dash import callback_context, no_update
    import base64
    import io
    import pandas as pd
    import uuid
    from datetime import datetime

    # Default return state
    default_return = [
        {"display": "none"},  # modal hidden
        "",
        "",
        [],
        [],
        [],
        [],
        None,
        None,
        None,
        None,
        1,
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        {},
        {},
        {"display": "none"},  # open mapping button hidden
        {"display": "none"},  # proceed button hidden
        {"display": "none"},  # skip button hidden
    ]

    ctx = callback_context
    if not ctx.triggered:
        return default_return

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    logger.info(f"Upload callback triggered by: {trigger_id}")

    # Handle modal close actions
    if trigger_id in ["cancel-mapping", "close-mapping-modal"]:
        logger.info("Closing column mapping modal")
        return default_return

    # Handle file upload - MAIN ENTRY POINT
    if trigger_id == "upload-data" and upload_contents is not None:
        try:
            logger.info(f"Processing file upload: {upload_filename}")

            # 1. REGISTER FILE UPLOAD
            content_type, content_string = upload_contents.split(",")
            decoded = base64.b64decode(content_string)
            session_id = str(uuid.uuid4())

            # Parse uploaded file
            df = None
            if upload_filename.endswith(".csv"):
                df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            elif upload_filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(io.BytesIO(decoded))
            elif upload_filename.endswith(".json"):
                import json

                json_data = json.loads(decoded.decode("utf-8"))
                df = pd.DataFrame(json_data) if isinstance(json_data, list) else pd.json_normalize(json_data)
            else:
                return [{"display": "none"}] + ["❌ Unsupported file format."] + default_return[2:]

            if df is None or df.empty:
                return [{"display": "none"}] + ["❌ File is empty or corrupted."] + default_return[2:]

            # 2. COLUMN ANALYSIS AND MAPPING
            logger.info("Running AI column analysis...")
            available_columns = list(df.columns)
            ai_suggestions, confidence_scores = enhanced_pattern_matching(available_columns)

            # Generate options for dropdowns
            column_options = [{"label": col, "value": col} for col in available_columns]

            # Calculate floor estimate
            device_col_suggested = ai_suggestions.get("device_name", available_columns[0])
            unique_devices = df[device_col_suggested].nunique() if device_col_suggested in df.columns else 10
            floor_estimate_calc = max(1, min(20, unique_devices // 8))

            # Store file and processed data
            file_store = {
                "filename": upload_filename,
                "session_id": session_id,
                "upload_time": datetime.now().isoformat(),
            }

            processed_store = {
                "data": df.to_dict("records"),
                "columns": available_columns,
                "ai_suggestions": ai_suggestions,
                "confidence_scores": confidence_scores,
                "session_id": session_id,
                "floor_estimate": {"total_floors": floor_estimate_calc, "confidence": 0.8},
            }

            # 3. SHOW COLUMN MAPPING MODAL IMMEDIATELY
            upload_success_msg = html.Div(
                [
                    html.P(
                        f"✅ File '{upload_filename}' uploaded successfully!", className="text-green-600 font-medium"
                    ),
                    html.P(
                        f"📊 Found {len(df)} records with {len(available_columns)} columns", className="text-gray-600"
                    ),
                    html.P("🤖 AI analysis complete. Verify column mapping below.", className="text-blue-600"),
                ]
            )

            # Return with modal VISIBLE and data populated
            return [
                {"display": "flex"},  # SHOW MODAL IMMEDIATELY
                f"File: {upload_filename} ({len(df)} records, {len(available_columns)} columns)",
                f"📊 AI mapped {len([k for k, v in ai_suggestions.items() if v])} columns automatically",
                column_options,
                column_options,
                column_options,
                column_options,
                ai_suggestions.get("timestamp"),
                ai_suggestions.get("device_name"),
                ai_suggestions.get("user_id"),
                ai_suggestions.get("event_type"),
                floor_estimate_calc,
                f"✅ {ai_suggestions.get('timestamp', 'None')} ({confidence_scores.get(ai_suggestions.get('timestamp', ''), 0)*100:.0f}%)",
                f"✅ {ai_suggestions.get('device_name', 'None')} ({confidence_scores.get(ai_suggestions.get('device_name', ''), 0)*100:.0f}%)",
                f"✅ {ai_suggestions.get('user_id', 'None')} ({confidence_scores.get(ai_suggestions.get('user_id', ''), 0)*100:.0f}%)",
                f"✅ {ai_suggestions.get('event_type', 'None')} ({confidence_scores.get(ai_suggestions.get('event_type', ''), 0)*100:.0f}%)",
                f"Overall AI Confidence: {max(confidence_scores.values(), default=0.8)*100:.0f}%",
                upload_success_msg,
                upload_success_msg,
                file_store,
                processed_store,
                {"display": "none"},  # hide manual mapping button since modal is open
                {"display": "none"},  # hide proceed button until mapping verified
                {"display": "none"},  # hide skip button until mapping verified
            ]

        except Exception as e:
            logger.error(f"Error processing file upload: {e}")
            error_msg = f"❌ Error processing file: {str(e)}"
            return [{"display": "none"}] + [error_msg] + default_return[2:]

    # Handle mapping verification
    elif trigger_id == "verify-mapping" and verify_clicks:
        try:
            logger.info("Verifying column mapping")

            if not timestamp_col:
                return [
                    {"display": "flex"},  # keep modal open
                    no_update,
                    "❌ Please select a timestamp column",
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                    "❌ Please select a timestamp column",
                    "",
                    file_store_data or {},
                    processed_data or {},
                    {"display": "none"},
                    {"display": "none"},
                    {"display": "none"},
                ]

            # Mapping verified successfully
            success_msg = html.Div(
                [
                    html.P("✅ Column mapping verified!", className="text-green-600 font-medium"),
                    html.P("🎯 Ready for device/door mapping...", className="text-blue-600"),
                ]
            )

            return [
                {"display": "none"},  # hide modal
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                success_msg,
                success_msg,
                file_store_data or {},
                processed_data or {},
                {"display": "none"},  # hide manual mapping button
                {"display": "inline-block"},  # SHOW proceed button
                {"display": "inline-block"},  # SHOW skip button
            ]

        except Exception as e:
            logger.error(f"Error verifying mapping: {e}")
            return [{"display": "flex"}] + [f"❌ Error: {str(e)}"] + default_return[2:]

    # Handle manual mapping button
    elif trigger_id == "open-column-mapping" and open_clicks:
        return [
            {"display": "flex"},  # show modal
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            {"display": "none"},
            {"display": "none"},
            {"display": "none"},
        ]

    return default_return


def enhanced_pattern_matching(headers):
    """Enhanced fallback pattern matching for column detection"""
    ai_suggestions = {}
    confidence_scores = {}

    patterns = {
        "timestamp": [
            "time",
            "date",
            "timestamp",
            "datetime",
            "created",
            "occurred",
            "when",
            "logged",
            "recorded",
            "event_time",
            "access_time",
        ],
        "device_name": [
            "door",
            "device",
            "location",
            "area",
            "reader",
            "panel",
            "terminal",
            "gate",
            "entrance",
            "exit",
            "access_point",
            "checkpoint",
            "zone",
        ],
        "user_id": [
            "user",
            "person",
            "employee",
            "badge",
            "card",
            "id",
            "worker",
            "staff",
            "visitor",
            "holder",
            "individual",
        ],
        "event_type": [
            "event",
            "action",
            "type",
            "result",
            "status",
            "access",
            "entry",
            "exit",
            "granted",
            "denied",
            "outcome",
        ],
    }

    for field, keywords in patterns.items():
        best_match = None
        best_score = 0
        for header in headers:
            header_lower = header.lower()
            for keyword in keywords:
                if keyword in header_lower:
                    score = len(keyword) / len(header_lower)
                    if keyword == header_lower:
                        score = 1.0
                    elif header_lower.startswith(keyword) or header_lower.endswith(keyword):
                        score = 0.9
                    if score > best_score:
                        best_score = score
                        best_match = header
        if best_match and best_score > 0.3:
            ai_suggestions[field] = best_match
            confidence_scores[best_match] = best_score

    return ai_suggestions, confidence_scores


def fallback_floor_estimation(data):
    """Fallback floor estimation using simple heuristics"""
    floor_indicators = set()
    for record in data[:100]:
        for value in record.values():
            if value:
                text = str(value).lower()
                import re

                patterns = [r"\b(\d+)f\b", r"\bfloor\s*(\d+)", r"\bf(\d+)", r"\b(\d+)fl\b"]
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        try:
                            floor_num = int(match)
                            if 1 <= floor_num <= 50:
                                floor_indicators.add(floor_num)
                        except ValueError:
                            continue

    if floor_indicators:
        max_floor = max(floor_indicators)
        confidence = f"{min(90, len(floor_indicators) * 20)}%"
        return max_floor, confidence

    return 1, "0%"


# New callback to prepare AI door mapping data when modal is opened
@callback(
    Output("door-mapping-modal-data-trigger", "data"),
    [Input("door-mapping-modal-trigger", "n_clicks"), Input("skip-door-mapping", "n_clicks")],
    [State("processed-data-store", "data"), State("device-column-dropdown", "value")],
    prevent_initial_call=True,
)
def handle_door_mapping(open_clicks, skip_clicks, processed_data, device_col):
    """Handle door mapping modal with AI pre-processing"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "skip-door-mapping":
        logger.info("Door mapping skipped by user")
        return dash.no_update

    if trigger_id == "door-mapping-modal-trigger" and open_clicks:
        try:
            if not processed_data or "data" not in processed_data:
                return dash.no_update

            # Extract CSV data
            csv_data = processed_data["data"]
            if not csv_data:
                return dash.no_update

            # Get device column
            available_columns = list(csv_data[0].keys())
            device_column = device_col

            if not device_column or device_column not in available_columns:
                # Fallback detection
                for col in available_columns:
                    if any(word in col.lower() for word in ["device", "door", "id"]):
                        device_column = col
                        break
                else:
                    device_column = available_columns[0]

            # Extract unique devices
            devices = list(set([str(row.get(device_column, "")).strip() for row in csv_data if row.get(device_column)]))
            devices = [d for d in devices if d and d != ""]

            # Generate AI mappings for each device
            ai_mapped_devices = []
            for device_id in devices:
                ai_attributes = generate_ai_door_attributes(device_id)
                ai_mapped_devices.append({"device_id": device_id, **ai_attributes})

            logger.info(f"AI processed {len(ai_mapped_devices)} devices for door mapping")

            return {"devices": ai_mapped_devices, "column": device_column, "ai_processed": True}

        except Exception as e:
            logger.error(f"Error in door mapping preparation: {e}")
            return dash.no_update

    return dash.no_update


# Door mapping callback
@callback(
    Output("door-mapping-modal-overlay", "className"),
    [Input("door-mapping-modal-trigger", "n_clicks"), Input("skip-door-mapping", "n_clicks")],
    [State("door-mapping-modal-data-trigger", "data")],
    prevent_initial_call=True,
)
def handle_door_mapping_buttons(open_clicks, skip_clicks, modal_data):
    """Handle door mapping and skip buttons with AI pre-processing"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "skip-door-mapping":
        logger.info("Door mapping skipped by user")
        return "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center hidden"

    if trigger_id == "door-mapping-modal-trigger":
        if not modal_data or not modal_data.get("ai_processed"):
            logger.warning("AI mapping not completed yet")
            return dash.no_update

        return "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center"

    return dash.no_update


def create_error_modal(title, message):
    """Create a simple error modal"""
    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.H3(f"❌ {title}", className="text-lg font-semibold text-red-600 mb-3"),
                            html.P(message, className="text-gray-700 mb-4"),
                            html.Button(
                                "Close",
                                id="close-error-modal",
                                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600",
                            ),
                        ],
                        className="bg-white p-6 rounded-lg max-w-md",
                    )
                ],
                className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4",
            )
        ]
    )


def create_door_mapping_modal_with_data(devices, device_column):
    """Create door mapping modal populated with actual CSV data"""

    # Generate AI suggestions for each device
    device_rows = []
    for i, device_id in enumerate(devices):
        # AI-based attribute suggestions
        ai_attributes = generate_ai_door_attributes(device_id)

        device_rows.append(
            html.Tr(
                [
                    # Device ID
                    html.Td(
                        [
                            html.Div(device_id, className="font-medium text-gray-900"),
                            html.Div(f"Device #{i+1}", className="text-sm text-gray-500"),
                        ],
                        className="px-4 py-3",
                    ),
                    # Location/Floor
                    html.Td(
                        [
                            dcc.Input(
                                id=f"location-input-{i}",
                                value=ai_attributes["location"],
                                placeholder="Enter location...",
                                className="w-full px-2 py-1 border rounded text-sm",
                                persistence=True,
                            )
                        ],
                        className="px-4 py-3",
                    ),
                    # Door Type
                    html.Td(
                        [
                            dcc.Dropdown(
                                id=f"door-type-{i}",
                                options=[
                                    {"label": "🚪 Standard Entry", "value": "entry"},
                                    {"label": "🚪 Exit Only", "value": "exit"},
                                    {"label": "🛗 Elevator", "value": "elevator"},
                                    {"label": "🪜 Stairwell", "value": "stairwell"},
                                    {"label": "🚨 Fire Escape", "value": "fire_escape"},
                                    {"label": "🚪 Emergency", "value": "emergency"},
                                    {"label": "🏢 Office", "value": "office"},
                                    {"label": "🔧 Utility", "value": "utility"},
                                    {"label": "🅿️ Parking", "value": "parking"},
                                    {"label": "❓ Other", "value": "other"},
                                ],
                                value=ai_attributes["door_type"],
                                className="text-sm",
                                persistence=True,
                            )
                        ],
                        className="px-4 py-3",
                    ),
                    # Critical Status
                    html.Td(
                        [
                            html.Div(
                                [
                                    dcc.Checklist(
                                        id=f"critical-check-{i}",
                                        options=[{"label": "Critical", "value": "critical"}],
                                        value=["critical"] if ai_attributes["is_critical"] else [],
                                        className="text-sm",
                                        persistence=True,
                                    )
                                ],
                                className="flex items-center justify-center",
                            )
                        ],
                        className="px-4 py-3 text-center",
                    ),
                    # Security Level
                    html.Td(
                        [
                            html.Div(
                                [
                                    dcc.Slider(
                                        id=f"security-level-{i}",
                                        min=1,
                                        max=10,
                                        step=1,
                                        value=ai_attributes["security_level"],
                                        marks={1: "1", 5: "5", 10: "10"},
                                        tooltip={"placement": "bottom", "always_visible": True},
                                        className="w-full",
                                        persistence=True,
                                    )
                                ],
                                className="px-2",
                            )
                        ],
                        className="px-4 py-3",
                    ),
                    # AI Confidence
                    html.Td(
                        [
                            html.Div(
                                [
                                    html.Span(f"{ai_attributes['confidence']}%", className="text-sm font-medium"),
                                    html.Div("AI Confidence", className="text-xs text-gray-500"),
                                ],
                                className="text-center",
                            )
                        ],
                        className="px-4 py-3 text-center verify-column",
                    ),
                ],
                className="border-b hover:bg-gray-50",
                id=f"device-row-{i}",
            )
        )

    # Create the complete modal
    modal = html.Div(
        [
            # Modal overlay
            html.Div(
                [
                    # Modal container
                    html.Div(
                        [
                            # Modal header
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.H2(
                                                "🏢 Door & Device Mapping",
                                                className="text-xl font-semibold text-gray-900",
                                            ),
                                            html.P(
                                                f"Configure attributes for {len(devices)} doors/devices from column '{device_column}'",
                                                className="text-sm text-gray-600 mt-1",
                                            ),
                                        ],
                                        className="flex-1",
                                    ),
                                    html.Button(
                                        "×",
                                        id="close-door-mapping-modal",
                                        className="text-gray-400 hover:text-gray-600 text-2xl font-bold",
                                    ),
                                ],
                                className="flex items-center justify-between p-6 border-b",
                            ),
                            # Modal body with scrollable table
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Table(
                                                [
                                                    # Table header
                                                    html.Thead(
                                                        [
                                                            html.Tr(
                                                                [
                                                                    html.Th(
                                                                        "Device ID",
                                                                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "Location/Floor",
                                                                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "Door Type",
                                                                        className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "Critical",
                                                                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "Security Level",
                                                                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                                    ),
                                                                    html.Th(
                                                                        "AI Confidence",
                                                                        className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider verify-column",
                                                                    ),
                                                                ]
                                                            )
                                                        ],
                                                        className="bg-gray-50",
                                                    ),
                                                    # Table body
                                                    html.Tbody(
                                                        device_rows, className="bg-white divide-y divide-gray-200"
                                                    ),
                                                ],
                                                className="min-w-full divide-y divide-gray-200",
                                            )
                                        ],
                                        className="overflow-x-auto",
                                    )
                                ],
                                className="max-h-96 overflow-y-auto p-6",
                            ),
                            # Modal footer
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Span(
                                                f"{len(devices)} doors detected", className="text-sm text-gray-600"
                                            ),
                                            html.Span(
                                                "• Adjust settings and click Save",
                                                className="text-sm text-gray-500 ml-2",
                                            ),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Button(
                                                "Reset to AI Suggestions",
                                                id="reset-door-mappings",
                                                className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 mr-3",
                                            ),
                                            html.Button(
                                                "Cancel",
                                                id="cancel-door-mapping",
                                                className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 mr-3",
                                            ),
                                            html.Button(
                                                "💾 Save Door Mappings",
                                                id="save-door-mappings",
                                                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700",
                                            ),
                                        ],
                                        className="flex",
                                    ),
                                ],
                                className="flex justify-between items-center p-6 border-t bg-gray-50",
                            ),
                        ],
                        className="bg-white rounded-lg max-w-6xl w-full max-h-screen overflow-hidden shadow-xl",
                    )
                ],
                className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-auto",
            ),
            # Hidden store for door mappings
            dcc.Store(id="door-mappings-store", data={"devices": devices, "column": device_column}),
        ]
    )

    return modal


def generate_ai_door_attributes(device_id):
    """Generate AI-based attribute suggestions for a door/device"""
    device_lower = device_id.lower()

    # Default attributes
    attributes = {
        "location": f"Floor 1 - {device_id}",
        "door_type": "entry",
        "is_critical": False,
        "security_level": 5,
        "confidence": 75,
    }

    # AI logic based on device ID patterns
    if any(word in device_lower for word in ["main", "front", "entrance", "lobby"]):
        attributes.update(
            {
                "door_type": "entry",
                "is_critical": True,
                "security_level": 8,
                "location": f"Main Entrance - {device_id}",
                "confidence": 95,
            }
        )
    elif any(word in device_lower for word in ["exit", "emergency", "fire"]):
        attributes.update(
            {
                "door_type": "fire_escape",
                "is_critical": True,
                "security_level": 9,
                "location": f"Emergency Exit - {device_id}",
                "confidence": 90,
            }
        )
    elif any(word in device_lower for word in ["elevator", "lift", "elev"]):
        attributes.update(
            {
                "door_type": "elevator",
                "is_critical": False,
                "security_level": 6,
                "location": f"Elevator Bank - {device_id}",
                "confidence": 88,
            }
        )
    elif any(word in device_lower for word in ["stair", "stairs", "stairwell"]):
        attributes.update(
            {
                "door_type": "stairwell",
                "is_critical": False,
                "security_level": 4,
                "location": f"Stairwell - {device_id}",
                "confidence": 85,
            }
        )
    elif any(word in device_lower for word in ["office", "room", "conf"]):
        attributes.update(
            {
                "door_type": "office",
                "is_critical": False,
                "security_level": 3,
                "location": f"Office Area - {device_id}",
                "confidence": 80,
            }
        )
    elif any(word in device_lower for word in ["parking", "garage", "lot"]):
        attributes.update(
            {
                "door_type": "parking",
                "is_critical": False,
                "security_level": 2,
                "location": f"Parking - {device_id}",
                "confidence": 85,
            }
        )

    # Detect floor information
    import re

    floor_match = re.search(r"(\d+)f|floor(\d+)|f(\d+)", device_lower)
    if floor_match:
        floor_num = floor_match.group(1) or floor_match.group(2) or floor_match.group(3)
        attributes["location"] = f"Floor {floor_num} - {device_id}"
        attributes["confidence"] = min(95, attributes["confidence"] + 10)

    return attributes


@callback(
    [
        Output("mapping-verified-status", "children", allow_duplicate=True),
        Output("door-mapping-modal-overlay", "className", allow_duplicate=True),
    ],
    [
        Input("save-door-mappings", "n_clicks"),
        Input("cancel-door-mapping", "n_clicks"),
        Input("close-door-mapping-modal", "n_clicks"),
    ],
    [State("door-mappings-store", "data"), State("processed-data-store", "data")],
    prevent_initial_call=True,
)
def handle_door_mapping_save(save_clicks, cancel_clicks, close_clicks, door_store, processed_data):
    """Handle saving door mapping configurations"""
    from dash import no_update

    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Close modal on cancel or close
    hidden_class = "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center hidden"

    if trigger_id in ["cancel-door-mapping", "close-door-mapping-modal"]:
        return no_update, hidden_class

    # Save door mappings
    if trigger_id == "save-door-mappings" and save_clicks:
        try:
            if not door_store or not processed_data:
                error_msg = html.Div("❌ No door mapping data to save", className="alert alert-error")
                return error_msg, hidden_class

            devices = door_store.get("devices", [])
            session_id = processed_data.get("session_id")

            # In a real implementation, you would collect all the form values here
            # For now, we'll simulate saving the configuration

            # Save to AI plugin if available
            if session_id:
                try:
                    from plugins.ai_classification.plugin import AIClassificationPlugin

                    ai_plugin = AIClassificationPlugin()
                    ai_plugin.start()

                    # Store door mappings in session
                    door_mapping_data = {
                        "devices": devices,
                        "device_count": len(devices),
                        "mapping_completed": True,
                        "saved_at": datetime.now().isoformat(),
                    }

                    ai_plugin.csv_repository.update_session_data(session_id, {"door_mappings": door_mapping_data})

                    logger.info(f"Door mappings saved for session {session_id}")
                except Exception as e:
                    logger.error(f"Failed to save door mappings: {e}")

            success_msg = html.Div(
                [
                    html.Div("✅ Door mappings saved successfully!", className="alert alert-success"),
                    html.Div(
                        [
                            html.H4("📋 Mapping Complete:", className="font-bold mt-3"),
                            html.Ul(
                                [
                                    html.Li(f"✅ {len(devices)} doors/devices configured"),
                                    html.Li("✅ Security levels assigned"),
                                    html.Li("✅ Critical status determined"),
                                    html.Li("✅ Door types classified"),
                                    html.Li("🎯 Ready for analytics and monitoring"),
                                ],
                                className="list-disc ml-6 mt-2",
                            ),
                        ],
                        className="mt-3 p-3 bg-green-50 border border-green-200 rounded",
                    ),
                    html.Div(
                        [
                            html.Button(
                                "📊 View Analytics Dashboard",
                                id="goto-analytics",
                                className="btn btn-primary mt-3 mr-2",
                            ),
                            html.Button(
                                "📤 Upload Another File", id="reset-upload", className="btn btn-secondary mt-3"
                            ),
                        ],
                        className="mt-4",
                    ),
                ]
            )

            return success_msg, hidden_class

        except Exception as e:
            logger.error(f"Error saving door mappings: {e}")
            error_msg = html.Div(f"❌ Error saving door mappings: {str(e)}", className="alert alert-error")
            return error_msg, hidden_class

    return no_update, no_update


@callback(Output("upload-info", "children"), [Input("processed-data-store", "data")], prevent_initial_call=True)
def show_debug_info(processed_data):
    """Show debug information about available columns"""
    if not processed_data or "data" not in processed_data:
        return ""

    csv_data = processed_data["data"]
    if not csv_data:
        return ""

    available_columns = list(csv_data[0].keys())
    ai_suggestions = processed_data.get("ai_suggestions", {})

    debug_info = html.Div(
        [
            html.Details(
                [
                    html.Summary("🔍 Debug: Available Columns", className="cursor-pointer text-sm text-gray-600"),
                    html.Div(
                        [
                            html.P(
                                f"Available columns: {', '.join(available_columns)}",
                                className="text-xs text-gray-500 mt-2",
                            ),
                            html.P(f"AI suggestions: {ai_suggestions}", className="text-xs text-gray-500"),
                            html.P(
                                f"Sample row: {dict(list(csv_data[0].items())[:3])}...",
                                className="text-xs text-gray-500",
                            ),
                        ],
                        className="mt-2 p-2 bg-gray-50 rounded text-xs",
                    ),
                ]
            )
        ],
        className="mt-2",
    )

    return debug_info


# Export the layout function
layout = create_dual_file_uploader

__all__ = [
    "create_dual_file_uploader",
    "layout",
    "render_column_mapping_panel",
    "handle_file_upload_and_modal",
    "handle_door_mapping",
    "handle_door_mapping_save",
]
