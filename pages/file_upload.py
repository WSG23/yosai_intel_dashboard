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
from dash import html, dcc
from dash.dash import no_update
from dash._callback import callback
from dash._callback_context import callback_context
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from services.device_learning_service import DeviceLearningService

from components.column_verification import (
    save_verified_mappings,
)


logger = logging.getLogger(__name__)

# Initialize device learning service
learning_service = DeviceLearningService()

# Global storage for uploaded data (in production, use database or session storage)
_uploaded_data_store: Dict[str, pd.DataFrame] = {}


def analyze_device_name_with_ai(device_name):
    """Check user inputs first, then AI"""
    from components.simple_device_mapping import _device_ai_mappings

    # If user has input for this device, use it
    if device_name in _device_ai_mappings and _device_ai_mappings[device_name].get('source') == 'user':
        return _device_ai_mappings[device_name]

    # Otherwise use AI
    try:
        from services.ai_device_generator import AIDeviceGenerator
        ai_gen = AIDeviceGenerator()
        result = ai_gen.generate_device_attributes(device_name)

        return {
            "floor_number": result.floor_number,
            "security_level": result.security_level,
            "confidence": result.confidence,
            "is_entry": result.is_entry,
            "is_exit": result.is_exit,
            "device_name": result.device_name,
            "ai_reasoning": result.ai_reasoning
        }
    except Exception:
        return {"floor_number": 1, "security_level": 5, "confidence": 0.1}


def layout():
    """File upload page layout with persistent storage"""
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
                                                            "Drag and Drop or Click to Upload",
                                                            className="text-primary",
                                                        ),
                                                        html.P(
                                                            "Supports CSV, Excel (.xlsx, .xls), and JSON files",
                                                            className="text-muted mb-0",
                                                        ),
                                                    ]
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
                ]
            ),
            # Upload results area
            dbc.Row([dbc.Col([html.Div(id="upload-results")])], className="mb-4"),
            # Data preview area
            dbc.Row([dbc.Col([html.Div(id="file-preview")])]),
            # Navigation to analytics
            dbc.Row([dbc.Col([html.Div(id="upload-nav")])]),
            # CRITICAL: Hidden placeholder buttons to prevent callback errors
            html.Div(
                [
                    dbc.Button(
                        "", id="verify-columns-btn-simple", style={"display": "none"}
                    ),
                    dbc.Button(
                        "", id="classify-devices-btn", style={"display": "none"}
                    ),
                ],
                style={"display": "none"},
            ),
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
                json_data = json.loads(decoded.decode("utf-8"))

                # Handle different JSON structures
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    if "data" in json_data:
                        df = pd.DataFrame(json_data["data"])
                    else:
                        df = pd.DataFrame([json_data])
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported JSON structure: {type(json_data)}",
                    }
            except json.JSONDecodeError as e:
                return {"success": False, "error": f"Invalid JSON format: {str(e)}"}
        else:
            return {
                "success": False,
                "error": f"Unsupported file type. Supported: .csv, .json, .xlsx, .xls",
            }

        # Validate the DataFrame
        if not isinstance(df, pd.DataFrame):
            return {
                "success": False,
                "error": f"Processing resulted in {type(df)} instead of DataFrame",
            }

        if df.empty:
            return {"success": False, "error": "File contains no data"}

        return {
            "success": True,
            "data": df,
            "rows": len(df),
            "columns": list(df.columns),
            "upload_time": datetime.now(),
        }

    except Exception as e:
        return {"success": False, "error": f"Error processing file: {str(e)}"}


def create_file_preview(df: pd.DataFrame, filename: str) -> dbc.Card | dbc.Alert:
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
                        dbc.Table.from_dataframe(  # type: ignore[attr-defined]
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


def get_ai_column_suggestions(columns: List[str]) -> Dict[str, Dict[str, Any]]:
    """Generate AI suggestions for column mapping"""
    suggestions = {}

    for col in columns:
        col_lower = col.lower().strip()

        if any(word in col_lower for word in ["time", "date", "stamp"]):
            suggestions[col] = {"field": "timestamp", "confidence": 0.8}
        elif any(word in col_lower for word in ["person", "user", "employee"]):
            suggestions[col] = {"field": "person_id", "confidence": 0.7}
        elif any(word in col_lower for word in ["door", "location", "device"]):
            suggestions[col] = {"field": "door_id", "confidence": 0.7}
        elif any(word in col_lower for word in ["access", "result", "status"]):
            suggestions[col] = {"field": "access_result", "confidence": 0.6}
        elif any(word in col_lower for word in ["token", "badge", "card"]):
            suggestions[col] = {"field": "token_id", "confidence": 0.6}
        else:
            suggestions[col] = {"field": "", "confidence": 0.0}

    return suggestions


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
        Input("url", "pathname"),
    ],
    [
        State("upload-data", "filename"),
        State({"type": "field-mapping", "column": ALL}, "value"),
        State({"type": "field-mapping", "column": ALL}, "id"),
        State("current-file-info-store", "data"),
        State("column-verification-modal", "is_open"),
        State("device-verification-modal", "is_open"),
    ],
    prevent_initial_call=False,
)
def consolidated_upload_callback(
    contents_list, verify_clicks, classify_clicks, confirm_clicks,
    cancel_col_clicks, cancel_dev_clicks, confirm_dev_clicks, pathname,
    filenames_list, dropdown_values, dropdown_ids, file_info,
    col_modal_open, dev_modal_open
):
    """Single consolidated callback that handles both upload and page restoration"""

    ctx = callback_context

    # Handle page load restoration FIRST
    if not ctx.triggered or ctx.triggered[0]['prop_id'] == 'url.pathname':
        if pathname == "/file-upload" and _uploaded_data_store:
            print(f"🔄 Restoring upload state for {len(_uploaded_data_store)} files")

            upload_results = []
            file_preview_components = []
            current_file_info = {}

            for filename, df in _uploaded_data_store.items():
                rows = len(df)
                cols = len(df.columns)

                upload_results.append(
                    dbc.Alert([
                        html.H6([
                            html.I(className="fas fa-check-circle me-2"),
                            f"Previously uploaded: {filename}"
                        ], className="alert-heading"),
                        html.P(f"📊 {rows:,} rows × {cols} columns"),
                    ], color="success", className="mb-3")
                )

                preview_df = df.head(5)
                file_preview_components.append(
                    html.Div([
                        dbc.Card([
                            dbc.CardHeader([
                                html.H6(f"📄 Data Preview: {filename}", className="mb-0")
                            ]),
                            dbc.CardBody([
                                html.H6("First 5 rows:"),
                                dbc.Table.from_dataframe(  # type: ignore[attr-defined]
                                    preview_df, striped=True, bordered=True, hover=True, size="sm"
                                ),
                                html.Hr(),
                                html.P([
                                    html.Strong("Columns: "),
                                    ", ".join(df.columns.tolist()[:10]),
                                    "..." if len(df.columns) > 10 else ""
                                ]),
                            ])
                        ], className="mb-3"),

                        dbc.Card([
                            dbc.CardHeader([html.H6("📋 Data Configuration", className="mb-0")]),
                            dbc.CardBody([
                                html.P("Configure your data for analysis:", className="mb-3"),
                                dbc.ButtonGroup([
                                    dbc.Button("📋 Verify Columns", id="verify-columns-btn-simple", color="primary", size="sm"),
                                    dbc.Button("🤖 Classify Devices", id="classify-devices-btn", color="info", size="sm"),
                                ], className="w-100"),
                            ])
                        ], className="mb-3")
                    ])
                )

                current_file_info = {
                    "filename": filename,
                    "rows": rows,
                    "columns": cols,
                    "column_names": df.columns.tolist(),
                    "ai_suggestions": get_ai_column_suggestions(df.columns.tolist())
                }

            upload_nav = html.Div([
                html.Hr(),
                html.H5("Ready to analyze?"),
                dbc.Button("🚀 Go to Analytics", href="/analytics", color="success", size="lg")
            ])

            return upload_results, file_preview_components, {}, upload_nav, current_file_info, False, False

        return no_update, no_update, no_update, no_update, no_update, no_update, no_update

    trigger_id = ctx.triggered[0]['prop_id']
    print(f"🎯 Callback triggered by: {trigger_id}")

    if "upload-data.contents" in trigger_id and contents_list:
        print("📁 Processing NEW file upload - clearing previous data...")
        _uploaded_data_store.clear()

        if not isinstance(contents_list, list):
            contents_list = [contents_list]
        if not isinstance(filenames_list, list):
            filenames_list = [filenames_list]

        upload_results = []
        file_preview_components = []
        file_info_dict = {}
        current_file_info = {}

        for content, filename in zip(contents_list, filenames_list):
            try:
                result = process_uploaded_file(content, filename)

                if result["success"]:
                    df = result["data"]
                    rows = len(df)
                    cols = len(df.columns)

                    _uploaded_data_store[filename] = df

                    upload_results.append(
                        dbc.Alert([
                            html.H6([
                                html.I(className="fas fa-check-circle me-2"),
                                f"Successfully uploaded {filename}"
                            ], className="alert-heading"),
                            html.P(f"📊 {rows:,} rows × {cols} columns processed"),
                        ], color="success", className="mb-3")
                    )

                    preview_df = df.head(5)
                    file_preview_components.append(
                        html.Div([
                            dbc.Card([
                                dbc.CardHeader([
                                    html.H6(f"📄 Data Preview: {filename}", className="mb-0")
                                ]),
                                dbc.CardBody([
                                    html.H6("First 5 rows:"),
                                    dbc.Table.from_dataframe(  # type: ignore[attr-defined]
                                        preview_df, striped=True, bordered=True, hover=True, size="sm"
                                    ),
                                    html.Hr(),
                                    html.P([html.Strong("Columns: "), ", ".join(df.columns.tolist()[:10])]),
                                ])
                            ], className="mb-3"),

                            dbc.Card([
                                dbc.CardHeader([html.H6("📋 Data Configuration", className="mb-0")]),
                                dbc.CardBody([
                                    html.P("Configure your data for analysis:", className="mb-3"),
                                    dbc.ButtonGroup([
                                        dbc.Button("📋 Verify Columns", id="verify-columns-btn-simple", color="primary", size="sm"),
                                        dbc.Button("🤖 Classify Devices", id="classify-devices-btn", color="info", size="sm"),
                                    ], className="w-100"),
                                ])
                            ], className="mb-3")
                        ])
                    )

                    column_names = df.columns.tolist()
                    file_info_dict[filename] = {
                        "filename": filename,
                        "rows": rows,
                        "columns": cols,
                        "column_names": column_names,
                        "upload_time": result["upload_time"].isoformat(),
                        "ai_suggestions": get_ai_column_suggestions(column_names)
                    }
                    current_file_info = file_info_dict[filename]

                else:
                    upload_results.append(
                        dbc.Alert([
                            html.H6("Upload Failed", className="alert-heading"),
                            html.P(result["error"]),
                        ], color="danger")
                    )

            except Exception as e:
                upload_results.append(
                    dbc.Alert(f"Error processing {filename}: {str(e)}", color="danger")
                )

        upload_nav = []
        if file_info_dict:
            upload_nav = html.Div([
                html.Hr(),
                html.H5("Ready to analyze?"),
                dbc.Button("🚀 Go to Analytics", href="/analytics", color="success", size="lg")
            ])

        return upload_results, file_preview_components, file_info_dict, upload_nav, current_file_info, no_update, no_update

    elif "verify-columns-btn-simple" in trigger_id and verify_clicks:
        print("🔍 Opening column verification modal...")
        return no_update, no_update, no_update, no_update, no_update, True, no_update

    elif "classify-devices-btn" in trigger_id and classify_clicks:
        print("🤖 Opening device classification modal...")
        return no_update, no_update, no_update, no_update, no_update, no_update, True

    elif "column-verify-confirm" in trigger_id and confirm_clicks:
        print("✅ Column mappings confirmed")
        success_alert = dbc.Toast([html.P("✅ Column mappings saved!")],
                                 header="Saved", is_open=True, dismissable=True, duration=3000)
        return success_alert, no_update, no_update, no_update, no_update, False, no_update

    elif "device-verify-confirm" in trigger_id and confirm_dev_clicks:
        print("✅ Device mappings confirmed")

        # ADD THESE 3 LINES FOR LEARNING:
        from services.consolidated_learning_service import get_learning_service
        learning_service = get_learning_service()
        fingerprint = learning_service.save_complete_mapping(_uploaded_data_store[list(_uploaded_data_store.keys())[0]], 
                                                            list(_uploaded_data_store.keys())[0], {})

        success_alert = dbc.Toast([html.P("✅ Device mappings saved!")],
                                 header="Saved", is_open=True, dismissable=True, duration=3000)
        return success_alert, no_update, no_update, no_update, no_update, no_update, False

    elif "column-verify-cancel" in trigger_id or "device-verify-cancel" in trigger_id:
        print("❌ Closing modals...")
        return no_update, no_update, no_update, no_update, no_update, False, False

    return no_update, no_update, no_update, no_update, no_update, no_update, no_update


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
        return [no_update]

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
    """Fixed device modal population - gets ALL devices WITH DEBUG"""
    if not is_open:
        return "Modal closed"

    print(f"🔧 Populating device modal...")

    try:
        uploaded_data = get_uploaded_data()
        if not uploaded_data:
            return dbc.Alert("No uploaded data found", color="warning")

        all_devices = set()
        device_columns = ["door_id", "device_name", "location", "door", "device"]

        for filename, df in uploaded_data.items():
            print(f"📄 Processing {filename} with {len(df)} rows")

            for col in df.columns:
                col_lower = col.lower().strip()
                if any(device_col in col_lower for device_col in device_columns):
                    unique_vals = df[col].dropna().unique()
                    all_devices.update(str(val) for val in unique_vals)
                    print(f"   Found {len(unique_vals)} devices in column '{col}'")

                    # ADD THIS DEBUG SECTION
                    print(f"🔍 DEBUG - First 10 device names from '{col}':")
                    sample_devices = unique_vals[:10]
                    for i, device in enumerate(sample_devices, 1):
                        print(f"   {i:2d}. {device}")

                    # TEST AI on sample devices
                    print(f"🤖 DEBUG - Testing AI on sample devices:")
                    try:
                        from services.ai_device_generator import AIDeviceGenerator
                        ai_gen = AIDeviceGenerator()

                        for device in sample_devices[:5]:  # Test first 5
                            try:
                                result = ai_gen.generate_device_attributes(str(device))
                                print(
                                    f"   🚪 '{device}' → Name: '{result.device_name}', Floor: {result.floor_number}, Security: {result.security_level}, Confidence: {result.confidence:.1%}"
                                )
                                print(
                                    f"      Access: Entry={result.is_entry}, Exit={result.is_exit}, Elevator={result.is_elevator}"
                                )
                                print(f"      Reasoning: {result.ai_reasoning}")
                            except Exception as e:
                                print(f"   ❌ AI error on '{device}': {e}")
                    except Exception as e:
                        print(f"🤖 DEBUG - AI import error: {e}")

        actual_devices = sorted(list(all_devices))
        print(f"🎯 Total unique devices found: {len(actual_devices)}")

        # Rest of your existing function...
        if not actual_devices:
            return dbc.Alert(
                [
                    html.H6("No devices detected"),
                    html.P(
                        "No device/door columns found in uploaded data. Expected columns: door_id, device_name, location, etc."
                    ),
                ],
                color="warning",
            )

        # Create device mapping table (your existing table creation code)
        table_rows = []
        for i, device_name in enumerate(actual_devices):
            ai_attributes = analyze_device_name_with_ai(device_name)

            table_rows.append(
                html.Tr(
                    [
                        html.Td(
                            [
                                html.Strong(device_name),
                                html.Br(),
                                html.Small(
                                    f"AI Confidence: {ai_attributes.get('confidence', 0.5):.0%}",
                                    className="text-success",
                                ),
                            ]
                        ),
                        html.Td(
                            [
                                dbc.Input(
                                    id={"type": "device-floor", "index": i},
                                    type="number",
                                    min=0,
                                    max=50,
                                    value=ai_attributes.get("floor_number", 1),
                                    placeholder="Floor",
                                    size="sm",
                                )
                            ]
                        ),
                        html.Td(
                            dbc.Checklist(
                                id={"type": "device-access", "index": i},
                                options=[
                                    {"label": "Entry", "value": "is_entry"},
                                    {"label": "Exit", "value": "is_exit"},
                                    {"label": "Elevator", "value": "is_elevator"},
                                    {"label": "Stairwell", "value": "is_stairwell"},
                                    {"label": "Fire Exit", "value": "is_fire_escape"},
                                ],
                                value=[
                                    k
                                    for k, v in ai_attributes.items()
                                    if k
                                    in [
                                        "is_entry",
                                        "is_exit",
                                        "is_elevator",
                                        "is_stairwell",
                                        "is_fire_escape",
                                    ]
                                    and v
                                ],
                                inline=False,
                            ),
                        ),
                        html.Td(
                            dbc.Input(
                                id={"type": "device-security", "index": i},
                                type="number",
                                min=0,
                                max=10,
                                value=ai_attributes.get("security_level", 5),
                                placeholder="0-10",
                                size="sm",
                            )
                        ),
                    ]
                )
            )

        # Return your existing table structure
        return dbc.Container(
            [
                dbc.Alert(
                    [
                        html.Strong("🤖 AI Analysis: "),
                        f"Analyzed {len(actual_devices)} devices. Check console for detailed AI debug info.",
                    ],
                    color="info",
                    className="mb-3",
                ),
                dbc.Table(
                    [
                        html.Thead(
                            [
                                html.Tr(
                                    [
                                        html.Th("Device Name"),
                                        html.Th("Floor"),
                                        html.Th("Access Types"),
                                        html.Th("Security Level"),
                                    ]
                                )
                            ]
                        ),
                        html.Tbody(table_rows),
                    ],
                    striped=True,
                    hover=True,
                ),
            ]
        )

    except Exception as e:
        print(f"❌ Error in device modal: {e}")
        return dbc.Alert(f"Error: {e}", color="danger")


@callback(
    Output("modal-body", "children", allow_duplicate=True),
    Input("column-verification-modal", "is_open"),
    State("current-file-info-store", "data"),
    prevent_initial_call=True,
)
def populate_modal_content(is_open, file_info):
    """Fixed modal content population"""
    if not is_open:
        return "Modal closed"

    if not file_info:
        return dbc.Alert("No file information available", color="warning")

    filename = file_info.get("filename", "Unknown")
    column_names = file_info.get("column_names", [])
    ai_suggestions = file_info.get("ai_suggestions", {})

    print(f"🔧 Populating column modal: {filename} with {len(column_names)} columns")
    print(f"   Columns: {column_names}")

    if not column_names:
        return dbc.Alert(f"No columns found in {filename}", color="warning")

    field_options = [
        {"label": "Person/User ID", "value": "person_id"},
        {"label": "Door/Location ID", "value": "door_id"},
        {"label": "Timestamp", "value": "timestamp"},
        {"label": "Access Result", "value": "access_result"},
        {"label": "Token/Badge ID", "value": "token_id"},
        {"label": "Event Type", "value": "event_type"},
        {"label": "Skip Column", "value": "ignore"},
    ]

    table_rows = []
    for i, column in enumerate(column_names):
        ai_suggestion = ai_suggestions.get(column, {})
        suggested_field = ai_suggestion.get("field", "")
        confidence = ai_suggestion.get("confidence", 0.0)

        table_rows.append(
            html.Tr(
                [
                    html.Td(
                        [
                            html.Strong(column),
                            html.Br(),
                            html.Small(
                                f"AI suggests: {suggested_field or 'None'} ({confidence:.0%})",
                                className="text-muted",
                            ),
                        ]
                    ),
                    html.Td(
                        [
                            dcc.Dropdown(
                                id={"type": "field-mapping", "column": column},
                                options=field_options,
                                value=suggested_field if confidence > 0.5 else None,
                                placeholder=f"Map {column} to...",
                                className="mb-2",
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
                [
                    "Select how each CSV column should map to analytics fields",
                    html.Br(),
                    f"Your CSV columns: {', '.join(column_names)}",
                ],
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
                    html.Tbody(table_rows),
                ],
                striped=True,
                className="mt-3",
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
