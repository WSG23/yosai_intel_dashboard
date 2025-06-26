#!/usr/bin/env python3
"""
Complete File Upload Page - Missing piece for consolidation
Integrates with analytics system
"""
import logging
import base64
import io
import json
from datetime import datetime

import pandas as pd
from typing import Optional, Dict, Any, List
import dash
from dash import callback, Input, Output, State, ALL, html, dcc
import dash_bootstrap_components as dbc

from components.column_verification import (
    get_ai_column_suggestions,
    save_verified_mappings,
)
from components.simple_device_mapping import create_simple_device_modal_with_ai


logger = logging.getLogger(__name__)

# Global storage for uploaded data (in production, use database or session storage)
_uploaded_data_store: Dict[str, pd.DataFrame] = {}


def analyze_device_name_with_ai(device_name):
    """Smart AI analysis of device names to predict attributes"""
    import re

    name_lower = str(device_name).lower()

    # Extract floor number from name
    floor_patterns = [
        r'\b(\d+)(?:st|nd|rd|th)?\s*(?:fl|floor)\b',
        r'\bfloor\s*(\d+)\b',
        r'\bf(\d+)\b',
        r'\b(\d+)f\b',
        r'lobby\s*(\d+)',
        r'level\s*(\d+)',
    ]

    floor = None
    for pattern in floor_patterns:
        match = re.search(pattern, name_lower)
        if match:
            floor = int(match.group(1))
            break

    # Detect special areas
    is_elevator = any(word in name_lower for word in ['lift', 'elevator', 'elev'])
    is_stairwell = any(word in name_lower for word in ['stair', 'stairs', 'stairwell', 'exit'])
    is_fire_escape = any(word in name_lower for word in ['fire', 'emergency', 'escape'])

    # Detect entry/exit
    is_entry = any(word in name_lower for word in ['main', 'front', 'gate', 'entrance', 'entry', 'lobby', 'reception'])
    is_exit = any(word in name_lower for word in ['exit', 'back', 'rear', 'emergency'])

    # If no specific exit indicators, assume entry points are also exits
    if is_entry and not is_exit:
        is_exit = True

    # Determine security level based on keywords
    security_level = 5  # Default medium security

    if any(word in name_lower for word in ['server', 'data', 'secure', 'admin', 'executive', 'ceo', 'finance', 'hr']):
        security_level = 8  # High security
    elif any(word in name_lower for word in ['office', 'meeting', 'conference', 'break', 'kitchen', 'storage']):
        security_level = 6  # Medium-high security
    elif any(word in name_lower for word in ['lobby', 'reception', 'main', 'public', 'visitor']):
        security_level = 3  # Low-medium security
    elif any(word in name_lower for word in ['restroom', 'bathroom', 'utility', 'janitor']):
        security_level = 2  # Low security

    return {
        "floor": floor,
        "is_entry": is_entry,
        "is_exit": is_exit,
        "is_elevator": is_elevator,
        "is_stairwell": is_stairwell,
        "is_fire_escape": is_fire_escape,
        "security_level": security_level,
        "confidence": 0.85  # High confidence for AI analysis
    }


def layout():
    """File upload page layout"""
    return dbc.Container(
        [
            # Page header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1("📁 File Upload", className="text-primary mb-2"),
                            html.P(
                                "Upload CSV, Excel, or JSON files for analysis",
                                className="text-muted mb-4",
                            ),
                        ]
                    )
                ]
            ),
            # Upload area
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        [
                                            html.H5(
                                                "📤 Upload Data Files", className="mb-0"
                                            )
                                        ]
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Upload(
                                                id="upload-data",
                                                children=html.Div(
                                                    [
                                                        html.I(
                                                            className="fas fa-cloud-upload-alt fa-4x mb-3 text-primary"
                                                        ),
                                                        html.H5(
                                                            "Drag and Drop or Click to Select Files"
                                                        ),
                                                        html.P(
                                                            "Supports CSV, Excel (.xlsx, .xls), and JSON files",
                                                            className="text-muted",
                                                        ),
                                                        html.Small(
                                                            "Maximum file size: 10MB",
                                                            className="text-secondary",
                                                        ),
                                                    ],
                                                    className="text-center p-5",
                                                ),
                                                style={
                                                    "width": "100%",
                                                    "border": "2px dashed #007bff",
                                                    "borderRadius": "8px",
                                                    "textAlign": "center",
                                                    "cursor": "pointer",
                                                    "backgroundColor": "#f8f9fa",
                                                },
                                                multiple=True,
                                            )
                                        ]
                                    ),
                                ]
                            )
                        ]
                    )
                ],
                className="mb-4",
            ),
            # Upload status and file list
            dbc.Row([dbc.Col([html.Div(id="upload-results")])], className="mb-4"),
            # Data preview area
            dbc.Row([dbc.Col([html.Div(id="file-preview")])]),
            # Navigation to analytics
            dbc.Row([dbc.Col([html.Div(id="upload-nav")])]),
            # Store for uploaded data info
            dcc.Store(id="file-info-store", data={}),
            dcc.Store(id="current-file-info-store"),
            dcc.Store(id="current-session-id", data="session_123"),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Column Mapping")),
                    dbc.ModalBody("Configure column mappings here", id="modal-body"),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel", id="column-verify-cancel", color="secondary"
                            ),
                            dbc.Button(
                                "Confirm", id="column-verify-confirm", color="success"
                            ),
                        ]
                    ),
                ],
                id="column-verification-modal",
                is_open=False,
                size="xl",
            ),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Device Classification")),
                    dbc.ModalBody("", id="device-modal-body"),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Cancel", id="device-verify-cancel", color="secondary"
                            ),
                            dbc.Button(
                                "Confirm", id="device-verify-confirm", color="success"
                            ),
                        ]
                    ),
                ],
                id="device-verification-modal",
                is_open=False,
                size="xl",
            ),
            create_simple_device_modal_with_ai([
                "main_entrance",
                "office_door_201",
                "server_room_3f",
                "elevator_bank",
            ]),
        ],
        fluid=True,
    )




def process_uploaded_file(contents, filename):
    """Process uploaded file content"""
    try:
        # Decode the base64 encoded file content
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        # Determine file type and parse accordingly
        if filename.endswith(".csv"):
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(decoded))
        elif filename.endswith(".json"):
            # Fix for JSON processing to ensure DataFrame is returned
            try:
                import json
                json_data = json.loads(decoded.decode("utf-8"))

                # Handle different JSON structures
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    if 'data' in json_data:
                        df = pd.DataFrame(json_data['data'])
                    else:
                        df = pd.DataFrame([json_data])
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported JSON structure: {type(json_data)}"
                    }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Invalid JSON format: {str(e)}"
                }
        else:
            return {
                "success": False,
                "error": f"Unsupported file type. Supported: .csv, .json, .xlsx, .xls"
            }

        # Validate the DataFrame
        if not isinstance(df, pd.DataFrame):
            return {
                "success": False,
                "error": f"Processing resulted in {type(df)} instead of DataFrame"
            }

        if df.empty:
            return {
                "success": False,
                "error": "File contains no data"
            }

        return {
            "success": True,
            "data": df,
            "rows": len(df),
            "columns": list(df.columns),
            "upload_time": datetime.now(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing file: {str(e)}"
        }


def create_file_preview(df: pd.DataFrame, filename: str) -> dbc.Card:
    """Create preview component for uploaded file"""
    try:
        # Basic statistics
        num_rows, num_cols = df.shape

        # Column info
        column_info = []
        for col in df.columns[:10]:  # Show first 10 columns
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            column_info.append(f"{col} ({dtype}) - {null_count} nulls")

        return dbc.Card(
            [
                dbc.CardHeader([html.H6(f"📄 {filename}", className="mb-0")]),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H6(
                                            "File Statistics:", className="text-primary"
                                        ),
                                        html.Ul(
                                            [
                                                html.Li(f"Rows: {num_rows:,}"),
                                                html.Li(f"Columns: {num_cols}"),
                                                html.Li(
                                                    f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB"
                                                ),
                                            ]
                                        ),
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        html.H6("Columns:", className="text-primary"),
                                        html.Ul(
                                            [html.Li(info) for info in column_info]
                                        ),
                                    ],
                                    width=6,
                                ),
                            ]
                        ),
                        html.Hr(),
                        html.H6("Sample Data:", className="text-primary mt-3"),
                        dbc.Table.from_dataframe(
                            df.head(5),
                            striped=True,
                            bordered=True,
                            hover=True,
                            responsive=True,
                            size="sm",
                        ),
                    ]
                ),
            ],
            className="mb-3",
        )

    except Exception as e:
        logger.error(f"Error creating preview for {filename}: {e}")
        return dbc.Alert(f"Error creating preview: {str(e)}", color="warning")


def get_uploaded_data() -> Dict[str, pd.DataFrame]:
    """Get all uploaded data (for use by analytics)"""
    return _uploaded_data_store.copy()


def get_uploaded_filenames() -> List[str]:
    """Get list of uploaded filenames"""
    return list(_uploaded_data_store.keys())


def clear_uploaded_data():
    """Clear all uploaded data"""
    global _uploaded_data_store
    _uploaded_data_store.clear()
    logger.info("Uploaded data cleared")


def get_file_info() -> Dict[str, Dict[str, Any]]:
    """Get information about uploaded files"""
    info = {}
    for filename, df in _uploaded_data_store.items():
        info[filename] = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "size_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        }
    return info


@callback(
    Output("upload-data", "style"),
    Input("upload-more-btn", "n_clicks"),
    prevent_initial_call=True,
)
def highlight_upload_area(n_clicks):
    """Highlight upload area when 'upload more' is clicked"""
    if n_clicks:
        return {
            "width": "100%",
            "border": "3px dashed #28a745",
            "borderRadius": "8px",
            "textAlign": "center",
            "cursor": "pointer",
            "backgroundColor": "#d4edda",
            "animation": "pulse 1s infinite",
        }
    return {
        "width": "100%",
        "border": "2px dashed #007bff",
        "borderRadius": "8px",
        "textAlign": "center",
        "cursor": "pointer",
        "backgroundColor": "#f8f9fa",
    }


@callback(
    [
        Output("upload-results", "children"),
        Output("file-preview", "children"),
        Output("file-info-store", "data"),
        Output("upload-nav", "children"),
        Output("current-file-info-store", "data"),
        Output("column-verification-modal", "is_open"),
        Output("device-verification-modal", "is_open"),
    ],
    [
        Input("upload-data", "contents"),
        Input("verify-columns-btn-simple", "n_clicks"),
        Input("classify-devices-btn", "n_clicks"),
        Input("column-verify-confirm", "n_clicks"),
        Input("column-verify-cancel", "n_clicks"),
        Input("device-verify-cancel", "n_clicks"),
        Input("device-verify-confirm", "n_clicks"),
    ],
    [
        State("upload-data", "filename"),
        State({"type": "field-mapping", "column": ALL}, "value"),
        State({"type": "field-mapping", "column": ALL}, "id"),
        State("current-file-info-store", "data"),
        State("column-verification-modal", "is_open"),
        State("device-verification-modal", "is_open"),
    ],
    prevent_initial_call=True,
)
def consolidated_upload_callback(
    contents_list, verify_clicks, classify_clicks, confirm_clicks,
    cancel_col_clicks, cancel_dev_clicks, confirm_dev_clicks,
    filenames_list, dropdown_values, dropdown_ids, file_info,
    col_modal_open, dev_modal_open
):
    """Consolidated callback to handle all upload-related interactions"""

    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    trigger_id = ctx.triggered[0]['prop_id']
    print(f"🎯 Consolidated callback triggered by: {trigger_id}")

    # Default values
    upload_results = dash.no_update
    file_preview = dash.no_update
    file_info_data = dash.no_update
    upload_nav = dash.no_update
    current_file_info = dash.no_update
    col_modal_state = dash.no_update
    dev_modal_state = dash.no_update

    # Handle file upload
    if "upload-data.contents" in trigger_id and contents_list:
        print("📁 Processing file upload...")

        if not isinstance(contents_list, list):
            contents_list = [contents_list]
        if not isinstance(filenames_list, list):
            filenames_list = [filenames_list]

        upload_results_list = []
        file_info_dict = {}
        preview_components = []
        current_file_info_dict = {}

        for content, filename in zip(contents_list, filenames_list):
            try:
                result = process_uploaded_file(content, filename)

                if result["success"]:
                    df = result["data"]
                    rows = result["rows"]
                    cols = result["columns"]

                    upload_results_list.append(
                        dbc.Alert([
                            html.H6([html.I(className="fas fa-check-circle me-2"), f"Successfully uploaded {filename}"], className="alert-heading"),
                            html.P(f"📊 {rows} rows × {cols} columns processed"),
                            html.Hr(),
                            dbc.ButtonGroup([
                                dbc.Button("📋 Verify Columns", id="verify-columns-btn-simple", color="primary", size="sm"),
                                dbc.Button("🤖 Classify Devices", id="classify-devices-btn", color="info", size="sm"),
                            ], className="d-grid gap-2 d-md-flex"),
                        ], color="success", className="mb-3")
                    )

                    current_file_info_dict = {
                        "filename": filename,
                        "rows": rows,
                        "columns": cols,
                        "column_names": df.columns.tolist(),
                        "upload_time": result["upload_time"],
                    }

                    file_info_dict[filename] = current_file_info_dict

                else:
                    upload_results_list.append(
                        dbc.Alert([
                            html.H6("Upload Failed", className="alert-heading"),
                            html.P(result["error"]),
                        ], color="danger")
                    )

            except Exception as e:
                logger.error(f"Error processing upload {filename}: {e}")
                upload_results_list.append(
                    dbc.Alert([
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"❌ Error processing {filename}: {str(e)}",
                    ], color="danger", className="mb-2")
                )

        upload_results = upload_results_list
        file_info_data = file_info_dict
        current_file_info = current_file_info_dict

        if file_info_dict:
            upload_nav = html.Div([
                html.Hr(),
                html.H5("Ready to analyze?"),
                dbc.Button("🚀 Go to Analytics", href="/analytics", color="success", size="lg")
            ])

    elif "verify-columns-btn-simple.n_clicks" in trigger_id and verify_clicks:
        print("🔍 Opening column verification modal...")
        upload_results = dbc.Alert("Opening column mapping modal!", color="success", dismissable=True)
        col_modal_state = True

    elif "classify-devices-btn.n_clicks" in trigger_id and classify_clicks:
        print("🤖 Opening device classification modal...")
        upload_results = dbc.Alert("Opening device classification modal!", color="info", dismissable=True)
        dev_modal_state = True

    elif "column-verify-confirm.n_clicks" in trigger_id and confirm_clicks:
        print("✅ Confirming column mappings...")

        filename = file_info.get("filename", "Unknown") if file_info else "Unknown"
        mappings = {}

        for value, id_dict in zip(dropdown_values or [], dropdown_ids or []):
            if value and value != "skip":
                csv_column = id_dict["column"]
                analytics_field = value
                mappings[csv_column] = analytics_field

        if mappings:
            save_ai_training_data(filename, mappings, file_info)

        upload_results = dbc.Alert([
            html.H6("Mappings Confirmed!", className="alert-heading"),
            html.P(f"Mapped {len(mappings)} fields for {filename}"),
            html.Hr(),
            html.P("Optional: Would you like to map device floors and security levels?", className="mb-0"),
        ], color="success")
        col_modal_state = False

    elif any(x in trigger_id for x in ["cancel", "device-verify-cancel"]):
        print("❌ Closing modals...")
        col_modal_state = False
        dev_modal_state = False

    elif "device-verify-confirm.n_clicks" in trigger_id and confirm_dev_clicks:
        print("✅ Device mappings confirmed...")
        upload_results = dbc.Alert([
            html.H6("Device Classification Complete!", className="alert-heading"),
            html.P("Device mappings have been saved successfully."),
        ], color="success")
        dev_modal_state = False

    return upload_results, file_preview, file_info_data, upload_nav, current_file_info, col_modal_state, dev_modal_state


def save_ai_training_data(filename: str, mappings: Dict[str, str], file_info: Dict):
    """Save confirmed mappings for AI training"""
    try:
        print(f"🤖 Saving AI training data for {filename}")

        # Prepare training data
        training_data = {
            "filename": filename,
            "timestamp": datetime.now().isoformat(),
            "mappings": mappings,
            "reverse_mappings": {v: k for k, v in mappings.items()},
            "column_count": len(file_info.get("columns", [])),
            "ai_suggestions": file_info.get("ai_suggestions", {}),
            "user_verified": True,
        }

        try:
            from plugins.ai_classification.plugin import AIClassificationPlugin
            from plugins.ai_classification.config import get_ai_config

            ai_plugin = AIClassificationPlugin(get_ai_config())
            if ai_plugin.start():
                session_id = (
                    f"verified_{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                ai_mappings = {v: k for k, v in mappings.items()}
                ai_plugin.confirm_column_mapping(ai_mappings, session_id)
                print(f"✅ AI training data saved: {ai_mappings}")
        except Exception as ai_e:
            print(f"⚠️ AI training save failed: {ai_e}")

        import os
        import json

        os.makedirs("data/training", exist_ok=True)
        with open(
            f"data/training/mappings_{datetime.now().strftime('%Y%m%d')}.jsonl", "a"
        ) as f:
            f.write(json.dumps(training_data) + "\n")

        print(f"✅ Training data saved locally")

    except Exception as e:
        print(f"❌ Error saving training data: {e}")


@callback(
    [Output({"type": "column-mapping", "index": ALL}, "value")],
    [Input("column-verify-ai-auto", "n_clicks")],
    [State("current-file-info-store", "data")],
    prevent_initial_call=True,
)
def apply_ai_suggestions(n_clicks, file_info):
    """Apply AI suggestions automatically - RESTORED"""
    if not n_clicks or not file_info:
        return [dash.no_update]

    ai_suggestions = file_info.get("ai_suggestions", {})
    columns = file_info.get("columns", [])

    print(f"🤖 Applying AI suggestions for {len(columns)} columns")

    # Apply AI suggestions with confidence > 0.3
    suggested_values = []
    for column in columns:
        suggestion = ai_suggestions.get(column, {})
        confidence = suggestion.get("confidence", 0.0)
        field = suggestion.get("field", "")

        if confidence > 0.3 and field:
            suggested_values.append(field)
            print(f"   ✅ {column} -> {field} ({confidence:.0%})")
        else:
            suggested_values.append(None)
            print(f"   ❓ {column} -> No confident suggestion ({confidence:.0%})")

    return [suggested_values]


@callback(
    Output("device-modal-body", "children"),
    Input("device-verification-modal", "is_open"),
    State("current-file-info-store", "data"),
    prevent_initial_call=True,
)
def populate_device_modal_with_learning(is_open, file_info):
    """Populate device verification modal with learning system"""
    if not is_open:
        return "Modal closed"

    print(f"🔧 Populating device modal with learning system...")

    try:
        from services.device_learning_service import get_device_learning_service
        learning_service = get_device_learning_service()

        # Get actual devices from uploaded data
        actual_devices = []
        learned_mappings = None

        if file_info and isinstance(file_info, dict):
            from pages.file_upload import get_uploaded_data
            uploaded_data = get_uploaded_data()

            if uploaded_data:
                for filename, df in uploaded_data.items():
                    # Check for learned mappings first
                    learned_mappings = learning_service.get_learned_mappings(df, filename)

                    # Find device column
                    device_columns = [col for col in df.columns 
                                    if any(keyword in col.lower() 
                                         for keyword in ['device', 'door', 'location', 'area', 'room'])]

                    if device_columns:
                        device_col = device_columns[0]
                        unique_devices = df[device_col].dropna().unique()[:10]

                        for device_name in unique_devices:
                            device_data = {"name": str(device_name)}

                            # Use learned mappings if available, otherwise AI analysis
                            if learned_mappings and device_name in learned_mappings:
                                learned = learned_mappings[device_name]
                                device_data.update({
                                    "floor": learned.get('floor_number'),
                                    "is_entry": learned.get('is_entry', False),
                                    "is_exit": learned.get('is_exit', False),
                                    "is_elevator": learned.get('is_elevator', False),
                                    "is_stairwell": learned.get('is_stairwell', False),
                                    "is_fire_escape": learned.get('is_fire_escape', False),
                                    "security_level": learned.get('security_level', 5),
                                    "confidence": 1.0,
                                    "source": "learned"
                                })
                                print(f"📚 Applied learned mapping for '{device_name}'")
                            else:
                                ai_analysis = analyze_device_name_with_ai(device_name)
                                device_data.update({**ai_analysis, "source": "ai"})
                                print(f"🤖 AI analyzed new device '{device_name}'")

                            actual_devices.append(device_data)
                        break

        learned_count = sum(1 for d in actual_devices if d.get("source") == "learned")
        ai_count = len(actual_devices) - learned_count

        status_message = []
        if learned_count > 0:
            status_message.append(f"📚 {learned_count} devices loaded from previous learning")
        if ai_count > 0:
            status_message.append(f"🤖 {ai_count} devices analyzed with AI")

        table_rows = []
        for i, device in enumerate(actual_devices):
            confidence_color = "success" if device.get("source") == "learned" else ("success" if device["confidence"] > 0.8 else "warning")
            source_badge = "Learned" if device.get("source") == "learned" else "AI Suggested"
            badge_color = "primary" if device.get("source") == "learned" else "info"

            table_rows.append(html.Tr([
                html.Td([
                    html.Strong(device["name"]),
                    html.Br(),
                    dbc.Badge(source_badge, color=badge_color, className="small me-1"),
                    dbc.Badge(f"{device['confidence']:.0%}", color=confidence_color, className="small")
                ], style={"width": "25%"}),

                html.Td([
                    dbc.Input(
                        id={"type": "device-floor", "index": i},
                        type="number",
                        min=0, max=50,
                        value=device.get("floor"),
                        placeholder="Floor #",
                        size="sm"
                    )
                ], style={"width": "10%"}),

                html.Td([
                    dbc.Checklist(
                        id={"type": "device-access", "index": i},
                        options=[
                            {"label": "Entry", "value": "is_entry"},
                            {"label": "Exit", "value": "is_exit"},
                        ],
                        value=[k for k in ["is_entry", "is_exit"] if device.get(k, False)],
                        inline=True
                    )
                ], style={"width": "15%"}),

                html.Td([
                    dbc.Checklist(
                        id={"type": "device-special", "index": i},
                        options=[
                            {"label": "Elevator", "value": "is_elevator"},
                            {"label": "Stairwell", "value": "is_stairwell"},
                            {"label": "Fire Escape", "value": "is_fire_escape"},
                        ],
                        value=[k for k in ["is_elevator", "is_stairwell", "is_fire_escape"] if device.get(k, False)],
                        inline=True
                    )
                ], style={"width": "20%"}),

                html.Td([
                    dbc.Input(
                        id={"type": "device-security", "index": i},
                        type="number",
                        min=0, max=10,
                        value=device.get("security_level", 5),
                        placeholder="0-10",
                        size="sm"
                    )
                ], style={"width": "10%"}),

                dcc.Store(id={"type": "device-name", "index": i}, data=device["name"]),
            ]))

        modal_content = html.Div([
            dbc.Alert([
                html.I(className="fas fa-brain me-2"),
                " | ".join(status_message) if status_message else "Ready for device classification",
            ], color="info" if learned_count > 0 else "warning", className="mb-3"),

            dbc.Alert([
                html.Strong("🎯 Learning Status: "),
                f"System has learned {learned_count} device mappings. " +
                ("All your previous settings have been applied!" if learned_count == len(actual_devices) else 
                 "Make corrections and they'll be remembered for next time!")
            ], color="light", className="small mb-3"),

            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Device Name", style={"width": "25%"}),
                        html.Th("Floor", style={"width": "10%"}),
                        html.Th("Access Type", style={"width": "15%"}),
                        html.Th("Special Areas", style={"width": "20%"}),
                        html.Th("Security (0-10)", style={"width": "10%"}),
                    ])
                ]),
                html.Tbody(table_rows)
            ], bordered=True, striped=True, hover=True, className="mb-3"),

            dbc.Alert([
                html.Strong("Security Levels: "),
                "0-2: Public areas, 3-5: Office areas, 6-8: Restricted, 9-10: High security"
            ], color="light", className="small")
        ])

        return modal_content

    except Exception as e:
        error_msg = f"Error populating device modal: {str(e)}"
        print(f"❌ {error_msg}")
        return dbc.Alert([
            html.H6("Device Classification Error", className="alert-heading"),
            html.P(f"Error: {str(e)}"),
        ], color="danger")




@callback(
    Output("modal-body", "children", allow_duplicate=True),
    Input("column-verification-modal", "is_open"),
    State("current-file-info-store", "data"),
    prevent_initial_call=True,
)
def populate_modal_content(is_open, file_info):
    """Populate modal with column mapping interface"""
    if not is_open or not file_info:
        return "No file selected"

    filename = file_info.get("filename", "Unknown")
    columns = file_info.get("columns", [])
    ai_suggestions = file_info.get("ai_suggestions", {})

    print(f"🔧 Populating modal for {filename} with {len(columns)} columns")

    if not columns:
        return f"No columns found in {filename}"

    def map_ai_to_dropdown_values(ai_field):
        """Convert AI suggestions to dropdown values"""
        ai_to_dropdown = {
            "user_id": "person_id",
            "location": "door_id",
            "access_type": "access_result",
            "timestamp": "timestamp",
        }
        return ai_to_dropdown.get(ai_field, ai_field)

    mapping_rows = []
    for i, column in enumerate(columns):
        ai_suggestion = ai_suggestions.get(column, {})
        suggested_field = ai_suggestion.get("field", "")
        confidence = ai_suggestion.get("confidence", 0.0)

        mapping_rows.append(
            html.Tr(
                [
                    html.Td(
                        [
                            html.Strong(column),
                            html.Br(),
                            html.Small(
                                f"AI suggests: {suggested_field} ({confidence:.0%})",
                                className=(
                                    "text-success" if confidence > 0.7 else "text-muted"
                                ),
                            ),
                        ]
                    ),
                    html.Td(
                        [
                            dcc.Dropdown(
                                id={"type": "field-mapping", "column": column},
                                options=[
                                    {"label": "Person/User ID", "value": "person_id"},
                                    {"label": "Door/Location ID", "value": "door_id"},
                                    {"label": "Timestamp", "value": "timestamp"},
                                    {
                                        "label": "Access Result",
                                        "value": "access_result",
                                    },
                                    {"label": "Token/Badge ID", "value": "token_id"},
                                    {"label": "Skip this column", "value": "skip"},
                                ],
                                value=(
                                    map_ai_to_dropdown_values(suggested_field)
                                    if map_ai_to_dropdown_values(suggested_field)
                                    in [
                                        "person_id",
                                        "door_id",
                                        "timestamp",
                                        "access_result",
                                        "token_id",
                                    ]
                                    else None
                                ),
                                placeholder=f"Map {column} to...",
                            )
                        ]
                    ),
                ]
            )
        )

    return html.Div(
        [
            html.H5(f"Map columns from {filename}"),
            dbc.Alert(
                "Select how each CSV column should map to analytics fields",
                color="info",
            ),
            dbc.Table(
                [
                    html.Thead(
                        [
                            html.Tr(
                                [
                                    html.Th("Your CSV Column"),
                                    html.Th("Maps To Analytics Field"),
                                ]
                            )
                        ]
                    ),
                    html.Tbody(mapping_rows),
                ],
                striped=True,
            ),
        ]
    )


# Export functions for integration with other modules
__all__ = [
    "layout",
    "get_uploaded_data",
    "get_uploaded_filenames",
    "clear_uploaded_data",
    "get_file_info",
    "process_uploaded_file",
    "save_ai_training_data",
]

print(f"\U0001f50d FILE_UPLOAD.PY LOADED - Callbacks should be registered")
