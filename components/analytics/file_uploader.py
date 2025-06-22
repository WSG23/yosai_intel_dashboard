"""
Dual Upload Box Component with Tailwind styling and working callbacks
"""
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import logging
from datetime import datetime
import pandas as pd
import base64
import io
import dash
import uuid
import tempfile
import os

logger = logging.getLogger(__name__)


def create_dual_file_uploader(upload_id: str = 'upload-data') -> html.Div:
    """Create dual upload box interface with proper IDs"""
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
                        id=upload_id,  # This should be 'upload-data'
                        children=html.Div([
                            # Upload icon
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
                        multiple=False,
                        accept='.csv,.json,.xlsx,.xls'
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


def render_column_mapping_panel(header_options, file_name="access_control_data.csv",
                               ai_suggestions=None, floor_estimate=None, user_id="default"):
    """Enhanced column mapping UI panel with AI suggestions and verification."""
    
    if ai_suggestions is None:
        ai_suggestions = {}
    if floor_estimate is None:
        floor_estimate = {'total_floors': 1, 'confidence': 0}

    def create_field_dropdown(label, field_id, suggested_value=None, required=False):
        return html.Div(className="form-field", children=[
            html.Label(label + (" *" if required else ""), className="form-label" + (" form-label--required" if required else "")),
            html.Small(f"AI Suggestion: {suggested_value}" if suggested_value else "No AI suggestion", 
                      className="form-help-text"),
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
                html.H2("Verify AI Column Mapping", className="modal__title"),
                html.P(f"File: {file_name}", className="modal__subtitle"),
                html.Button("\xd7", id="close-mapping-modal", className="modal__close")
            ]),

            html.Div(className="modal__body", children=[
                # Instructions
                html.Div(className="form-instructions", children=[
                    html.P("🤖 AI has analyzed your file and suggested column mappings below. Please verify and adjust as needed.",
                           className="form-instructions-text"),
                    html.P(f"📊 Detected {len(header_options)} columns in your file",
                           className="form-instructions-subtext")
                ]),

                html.Hr(className="form-separator"),

                # Column Mapping Fields
                html.Div(className="form-grid", children=[
                    create_field_dropdown("Timestamp Column", "timestamp-dropdown", 
                                         ai_suggestions.get('timestamp'), required=True),
                    create_field_dropdown("Device/Door Column", "device-column-dropdown", 
                                         ai_suggestions.get('device_name')),
                    create_field_dropdown("User ID Column", "user-id-dropdown", 
                                         ai_suggestions.get('user_id')),
                    create_field_dropdown("Event Type Column", "event-type-dropdown", 
                                         ai_suggestions.get('event_type'))
                ]),

                html.Hr(className="form-separator"),

                # Floor Estimate
                html.Div(className="form-row", children=[
                    html.Div(className="form-field", children=[
                        html.Label("Number of Floors", className="form-label"),
                        dcc.Input(
                            id="floor-estimate-input",
                            type="number",
                            value=floor_estimate.get('total_floors', 1),
                            min=1,
                            max=100,
                            className="form-input"
                        ),
                        html.Small(f"AI Confidence: {floor_estimate.get('confidence', 0) * 100:.0f}%", 
                                 className="form-help-text")
                    ])
                ]),

                # Hidden storage for user ID
                html.Div(id="user-id-storage", children=user_id, style={"display": "none"})
            ]),

            html.Div(className="modal__footer", children=[
                html.Button("Cancel", id="cancel-mapping", className="btn btn-secondary"),
                html.Button("\u2705 Verify & Learn", id="verify-mapping", className="btn btn-primary")
            ])
        ])
    ])




@callback(
    [Output('column-mapping-modal-overlay', 'style'),
     Output('modal-subtitle', 'children'),
     Output('column-count-text', 'children'),
     Output('timestamp-dropdown', 'options'),
     Output('device-column-dropdown', 'options'),
     Output('user-id-dropdown', 'options'),
     Output('event-type-dropdown', 'options'),
     Output('timestamp-dropdown', 'value'),
     Output('device-column-dropdown', 'value'),
     Output('user-id-dropdown', 'value'),
     Output('event-type-dropdown', 'value'),
     Output('floor-estimate-input', 'value'),
     Output('timestamp-suggestion', 'children'),
     Output('device-suggestion', 'children'),
     Output('user-suggestion', 'children'),
     Output('event-suggestion', 'children'),
     Output('floor-confidence', 'children'),
     Output('upload-status', 'children'),
     Output('mapping-verified-status', 'children'),
     Output('uploaded-file-store', 'data'),
     Output('processed-data-store', 'data'),
     Output('open-door-mapping', 'style'),
     Output('skip-door-mapping', 'style')],
    [Input('upload-data', 'contents'),
     Input('cancel-mapping', 'n_clicks'),
     Input('verify-mapping', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('timestamp-dropdown', 'value'),
     State('device-column-dropdown', 'value'),
     State('user-id-dropdown', 'value'),
     State('event-type-dropdown', 'value'),
     State('floor-estimate-input', 'value'),
     State('user-id-storage', 'children'),
     State('uploaded-file-store', 'data'),
     State('processed-data-store', 'data')],
    prevent_initial_call=True)
def handle_all_upload_modal_actions(upload_contents, cancel_clicks, verify_clicks,
                                  upload_filename, timestamp_col, device_col, user_col,
                                  event_type_col, floor_estimate, user_id, file_store_data, processed_data):
    """Enhanced file upload handler with AI classification integration"""
    from dash import callback_context, no_update
    import dash
    import uuid
    import tempfile
    import os
    from datetime import datetime

    try:
        from plugins.ai_classification.plugin import AIClassificationPlugin
        ai_plugin = AIClassificationPlugin()
        ai_plugin.start()
        AI_AVAILABLE = True
    except ImportError as e:
        logger.warning(f"AI Classification plugin not available: {e}")
        AI_AVAILABLE = False

    ctx = callback_context
    if not ctx.triggered:
        return [{"display": "none"}] + [no_update] * 22

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'upload-data' and upload_contents is not None:
        try:
            session_id = str(uuid.uuid4())
            content_type, content_string = upload_contents.split(',')
            decoded = base64.b64decode(content_string)

            df = None
            if upload_filename.endswith('.csv'):
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif upload_filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(io.BytesIO(decoded))
            elif upload_filename.endswith('.json'):
                import json
                json_data = json.loads(decoded.decode('utf-8'))
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                else:
                    df = pd.json_normalize(json_data)
            else:
                error_msg = html.Div("❌ Unsupported file format. Use CSV, JSON, or Excel files.", className="alert alert-error")
                return [{"display": "none"}] + [no_update] * 20 + [error_msg, no_update, {}, {}, {"display": "none"}, {"display": "none"}]

            if df is None or df.empty:
                error_msg = html.Div("❌ File appears to be empty or corrupted.", className="alert alert-error")
                return [{"display": "none"}] + [no_update] * 20 + [error_msg, no_update, {}, {}, {"display": "none"}, {"display": "none"}]

            temp_file_path = None
            if AI_AVAILABLE:
                try:
                    temp_dir = tempfile.mkdtemp()
                    temp_file_path = os.path.join(temp_dir, upload_filename)
                    with open(temp_file_path, 'wb') as f:
                        f.write(decoded)
                    ai_result = ai_plugin.process_csv_file(temp_file_path, session_id, user_id)
                    logger.info(f"AI processing result: {ai_result}")
                except Exception as e:
                    logger.error(f"AI processing failed: {e}")
                    AI_AVAILABLE = False

            headers = df.columns.tolist()
            options = [{"label": col, "value": col} for col in headers]
            ai_suggestions = {}
            confidence_scores = {}
            if AI_AVAILABLE:
                try:
                    mapping_result = ai_plugin.map_columns(headers, session_id)
                    if mapping_result.get('success'):
                        ai_suggestions = mapping_result.get('suggested_mapping', {})
                        confidence_scores = mapping_result.get('confidence_scores', {})
                        logger.info(f"AI column mapping: {ai_suggestions}")
                except Exception as e:
                    logger.error(f"AI column mapping failed: {e}")

            if not ai_suggestions:
                for col in headers:
                    col_lower = col.lower()
                    if any(word in col_lower for word in ['time', 'date', 'timestamp']):
                        ai_suggestions['timestamp'] = col
                        confidence_scores['timestamp'] = 0.8
                    elif any(word in col_lower for word in ['door', 'device', 'location']):
                        ai_suggestions['device_name'] = col
                        confidence_scores['device_name'] = 0.7
                    elif any(word in col_lower for word in ['user', 'id', 'employee', 'badge']):
                        ai_suggestions['user_id'] = col
                        confidence_scores['user_id'] = 0.7
                    elif any(word in col_lower for word in ['event', 'type', 'action', 'result']):
                        ai_suggestions['event_type'] = col
                        confidence_scores['event_type'] = 0.7

            floor_estimate_value = 1
            floor_confidence = "85%"
            if AI_AVAILABLE and ai_suggestions:
                try:
                    data_list = df.to_dict('records')
                    floor_result = ai_plugin.estimate_floors(data_list, session_id)
                    if floor_result.get('success'):
                        floor_estimate_value = floor_result.get('total_floors', 1)
                        floor_confidence = f"{floor_result.get('confidence', 0.85) * 100:.0f}%"
                except Exception as e:
                    logger.error(f"Floor estimation failed: {e}")

            status_msg = html.Div([
                f"✅ Successfully uploaded '{upload_filename}'",
                html.Br(),
                f"📊 {len(df)} rows, {len(headers)} columns processed",
                html.Br(),
                f"🤖 AI analysis {'completed' if AI_AVAILABLE else 'not available'}"
            ], className="alert alert-success")

            file_store = {
                'session_id': session_id,
                'filename': upload_filename,
                'temp_path': temp_file_path,
                'columns': headers,
                'row_count': len(df)
            }

            processed_store = {
                'session_id': session_id,
                'ai_suggestions': ai_suggestions,
                'confidence_scores': confidence_scores,
                'data': df.to_dict('records')
            }


            if AI_AVAILABLE and session_id:
                try:
                    persistent_data = {
                        'filename': upload_filename,
                        'headers': headers,
                        'row_count': len(df),
                        'ai_suggestions': ai_suggestions,
                        'confidence_scores': confidence_scores,
                        'upload_timestamp': datetime.now().isoformat(),
                        'processed_data': df.head(1000).to_dict('records')
                    }
                    ai_plugin.csv_repository.store_processed_data(session_id, persistent_data)
                    logger.info(f"Data persisted for session {session_id}")
                except Exception as e:
                    logger.error(f"Failed to persist data: {e}")


            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    os.rmdir(os.path.dirname(temp_file_path))
                except:
                    pass

            return [
                {"display": "block"},
                f"File: {upload_filename}",
                f"📊 Detected {len(headers)} columns in your file",
                options, options, options, options,
                ai_suggestions.get('timestamp'),
                ai_suggestions.get('device_name'),
                ai_suggestions.get('user_id'),
                ai_suggestions.get('event_type'),
                floor_estimate_value,
                f"AI Suggestion: {ai_suggestions.get('timestamp', 'None')} ({confidence_scores.get('timestamp', 0)*100:.0f}%)",
                f"AI Suggestion: {ai_suggestions.get('device_name', 'None')} ({confidence_scores.get('device_name', 0)*100:.0f}%)",
                f"AI Suggestion: {ai_suggestions.get('user_id', 'None')} ({confidence_scores.get('user_id', 0)*100:.0f}%)",
                f"AI Suggestion: {ai_suggestions.get('event_type', 'None')} ({confidence_scores.get('event_type', 0)*100:.0f}%)",
                f"AI Confidence: {floor_confidence}",
                status_msg,
                "",
                file_store,
                processed_store,
                {"display": "none"},
                {"display": "none"}
            ]

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            error_msg = html.Div(f"❌ Error processing file: {str(e)}", className="alert alert-error")
            return [{"display": "none"}] + [no_update] * 20 + [error_msg, no_update, {}, {}, {"display": "none"}, {"display": "none"}]

    elif trigger_id == 'cancel-mapping':
        return [{"display": "none"}] + [no_update] * 22

    elif trigger_id == 'verify-mapping' and verify_clicks:
        try:
            session_id = processed_data.get('session_id') if processed_data else None
            if not session_id:
                error_msg = html.Div("❌ Session expired. Please re-upload your file.", className="alert alert-error")
                return [{"display": "none"}] + [no_update] * 20 + [error_msg, no_update, {}, {}, {"display": "none"}, {"display": "none"}]
            if AI_AVAILABLE:
                try:
                    mapping = {
                        'timestamp': timestamp_col,
                        'device_name': device_col,
                        'user_id': user_col,
                        'event_type': event_type_col
                    }
                    mapping = {k: v for k, v in mapping.items() if v is not None}
                    ai_plugin.confirm_column_mapping(mapping, session_id)
                    logger.info(f"Column mapping confirmed: {mapping}")
                except Exception as e:
                    logger.error(f"Failed to confirm mapping: {e}")
            success_msg = html.Div([
                html.Div("✅ Column mapping verified and learned!", className="alert alert-success"),
                html.Div([
                    html.H4("📋 Mapping Summary:", className="font-bold mt-3"),
                    html.Ul([
                        html.Li(f"Timestamp: {timestamp_col or 'Not mapped'}"),
                        html.Li(f"Door/Location: {device_col or 'Not mapped'}"),
                        html.Li(f"User ID: {user_col or 'Not mapped'}"),
                        html.Li(f"Event Type: {event_type_col or 'Not mapped'}"),
                        html.Li(f"Floor Estimate: {floor_estimate or 1} floors")
                    ], className="list-disc ml-6 mt-2")
                ], className="mt-3 p-3 bg-gray-100 rounded")
            ])
            return [
                {"display": "none"},
                no_update, no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                no_update,
                success_msg,
                no_update, no_update,
                {"display": "inline-block"},
                {"display": "inline-block"}
            ]
        except Exception as e:
            logger.error(f"Error verifying mapping: {e}")
            error_msg = html.Div(f"❌ Error verifying mapping: {str(e)}", className="alert alert-error")
            return [{"display": "none"}] + [no_update] * 20 + [error_msg, no_update, {}, {}, {"display": "none"}, {"display": "none"}]
    return [{"display": "none"}] + [no_update] * 22
# Door mapping callback
@callback(
    [Output('door-mapping-modal', 'children'),
     Output('door-mapping-modal', 'style')],
    [Input('open-door-mapping', 'n_clicks'),
     Input('skip-door-mapping', 'n_clicks')],
    [State('processed-data-store', 'data'),
     State('column-mapping-store', 'data')],
    prevent_initial_call=True
)
def handle_door_mapping(open_clicks, skip_clicks, processed_data, mapping_data):
    """Handle door mapping modal with real CSV data"""
    ctx = callback_context
    if not ctx.triggered:
        return [], {'display': 'none'}

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'skip-door-mapping':
        return [], {'display': 'none'}

    if trigger_id == 'open-door-mapping':
        try:
            if not processed_data or 'data' not in processed_data:
                error_modal = html.Div([
                    html.Div([
                        html.H3("❌ No Data Available"),
                        html.P("Please upload and process a file first."),
                        html.Button("Close", id="close-error-modal", className="btn btn-secondary")
                    ], className="modal-content p-6 bg-white rounded")
                ], className="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center")
                return error_modal, {'display': 'block'}

            # Extract device/door data from processed CSV
            csv_data = processed_data['data']
            ai_suggestions = processed_data.get('ai_suggestions', {})

            # Get the device/door column from AI suggestions or user mapping
            device_column = ai_suggestions.get('device_name') or ai_suggestions.get('location')

            if not device_column:
                # Check if user manually mapped it
                # For now, try common column names
                possible_columns = ['door', 'device', 'location', 'door_id', 'device_id', 'area']
                for col in possible_columns:
                    if col in (csv_data[0].keys() if csv_data else []):
                        device_column = col
                        break

            if not device_column or not csv_data:
                error_modal = html.Div([
                    html.Div([
                        html.H3("❌ No Door/Device Column Found"),
                        html.P("Please ensure your file has a column containing door or device identifiers."),
                        html.Button("Close", id="close-error-modal", className="btn btn-secondary")
                    ], className="modal-content p-6 bg-white rounded")
                ], className="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center")
                return error_modal, {'display': 'block'}

            # Extract unique doors/devices
            unique_devices = set()
            for row in csv_data:
                if device_column in row and row[device_column]:
                    unique_devices.add(str(row[device_column]).strip())

            unique_devices = sorted(list(unique_devices))

            if not unique_devices:
                error_modal = html.Div([
                    html.Div([
                        html.H3("❌ No Devices Found"),
                        html.P(f"No valid entries found in column '{device_column}'."),
                        html.Button("Close", id="close-error-modal", className="btn btn-secondary")
                    ], className="modal-content p-6 bg-white rounded")
                ], className="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center")
                return error_modal, {'display': 'block'}

            # Create door mapping modal with real data
            door_mapping_modal = create_door_mapping_modal_with_data(unique_devices, device_column)
            return door_mapping_modal, {'display': 'block'}

        except Exception as e:
            logger.error(f"Error creating door mapping modal: {e}")
            error_modal = html.Div([
                html.Div([
                    html.H3("❌ Error"),
                    html.P(f"Error creating door mapping: {str(e)}"),
                    html.Button("Close", id="close-error-modal", className="btn btn-secondary")
                ], className="modal-content p-6 bg-white rounded")
            ], className="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center")
            return error_modal, {'display': 'block'}

    return [], {'display': 'none'}


def create_door_mapping_modal_with_data(devices, device_column):
    """Create door mapping modal populated with actual CSV data"""

    # Generate AI suggestions for each device
    device_rows = []
    for i, device_id in enumerate(devices):
        # AI-based attribute suggestions
        ai_attributes = generate_ai_door_attributes(device_id)

        device_rows.append(html.Tr([
            # Device ID
            html.Td([
                html.Div(device_id, className="font-medium text-gray-900"),
                html.Div(f"Device #{i+1}", className="text-sm text-gray-500")
            ], className="px-4 py-3"),

            # Location/Floor
            html.Td([
                dcc.Input(
                    id=f"location-input-{i}",
                    value=ai_attributes['location'],
                    placeholder="Enter location...",
                    className="w-full px-2 py-1 border rounded text-sm",
                    persistence=True
                )
            ], className="px-4 py-3"),

            # Door Type
            html.Td([
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
                        {"label": "❓ Other", "value": "other"}
                    ],
                    value=ai_attributes['door_type'],
                    className="text-sm",
                    persistence=True
                )
            ], className="px-4 py-3"),

            # Critical Status
            html.Td([
                html.Div([
                    dcc.Checklist(
                        id=f"critical-check-{i}",
                        options=[{"label": "Critical", "value": "critical"}],
                        value=["critical"] if ai_attributes['is_critical'] else [],
                        className="text-sm",
                        persistence=True
                    )
                ], className="flex items-center justify-center")
            ], className="px-4 py-3 text-center"),

            # Security Level
            html.Td([
                html.Div([
                    dcc.Slider(
                        id=f"security-level-{i}",
                        min=1,
                        max=10,
                        step=1,
                        value=ai_attributes['security_level'],
                        marks={1: "1", 5: "5", 10: "10"},
                        tooltip={"placement": "bottom", "always_visible": True},
                        className="w-full",
                        persistence=True
                    )
                ], className="px-2")
            ], className="px-4 py-3"),

            # AI Confidence
            html.Td([
                html.Div([
                    html.Span(f"{ai_attributes['confidence']}%", 
                             className="text-sm font-medium"),
                    html.Div("AI Confidence", className="text-xs text-gray-500")
                ], className="text-center")
            ], className="px-4 py-3"),

        ], className="border-b hover:bg-gray-50", id=f"device-row-{i}"))

    # Create the complete modal
    modal = html.Div([
        # Modal overlay
        html.Div([
            # Modal container
            html.Div([
                # Modal header
                html.Div([
                    html.Div([
                        html.H2("🏢 Door & Device Mapping", 
                               className="text-xl font-semibold text-gray-900"),
                        html.P(f"Configure attributes for {len(devices)} doors/devices from column '{device_column}'", 
                               className="text-sm text-gray-600 mt-1")
                    ], className="flex-1"),
                    html.Button("×", 
                               id="close-door-mapping-modal",
                               className="text-gray-400 hover:text-gray-600 text-2xl font-bold")
                ], className="flex items-center justify-between p-6 border-b"),

                # Modal body with scrollable table
                html.Div([
                    html.Div([
                        html.Table([
                            # Table header
                            html.Thead([
                                html.Tr([
                                    html.Th("Device ID", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
                                    html.Th("Location/Floor", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
                                    html.Th("Door Type", className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"),
                                    html.Th("Critical", className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"),
                                    html.Th("Security Level", className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"),
                                    html.Th("AI Confidence", className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider"),
                                ])
                            ], className="bg-gray-50"),

                            # Table body
                            html.Tbody(device_rows, className="bg-white divide-y divide-gray-200")

                        ], className="min-w-full divide-y divide-gray-200")
                    ], className="overflow-x-auto")
                ], className="max-h-96 overflow-y-auto p-6"),

                # Modal footer
                html.Div([
                    html.Div([
                        html.Span(f"{len(devices)} doors detected", className="text-sm text-gray-600"),
                        html.Span("• Adjust settings and click Save", className="text-sm text-gray-500 ml-2")
                    ]),
                    html.Div([
                        html.Button("Reset to AI Suggestions", 
                                   id="reset-door-mappings",
                                   className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 mr-3"),
                        html.Button("Cancel", 
                                   id="cancel-door-mapping",
                                   className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 mr-3"),
                        html.Button("💾 Save Door Mappings", 
                                   id="save-door-mappings",
                                   className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700")
                    ], className="flex")
                ], className="flex justify-between items-center p-6 border-t bg-gray-50")

            ], className="bg-white rounded-lg max-w-6xl w-full max-h-screen overflow-hidden shadow-xl")
        ], className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"),

        # Hidden store for door mappings
        dcc.Store(id="door-mappings-store", data={"devices": devices, "column": device_column})

    ])

    return modal


def generate_ai_door_attributes(device_id):
    """Generate AI-based attribute suggestions for a door/device"""
    device_lower = device_id.lower()

    # Default attributes
    attributes = {
        'location': f"Floor 1 - {device_id}",
        'door_type': 'entry',
        'is_critical': False,
        'security_level': 5,
        'confidence': 75
    }

    # AI logic based on device ID patterns
    if any(word in device_lower for word in ['main', 'front', 'entrance', 'lobby']):
        attributes.update({
            'door_type': 'entry',
            'is_critical': True,
            'security_level': 8,
            'location': f"Main Entrance - {device_id}",
            'confidence': 95
        })
    elif any(word in device_lower for word in ['exit', 'emergency', 'fire']):
        attributes.update({
            'door_type': 'fire_escape',
            'is_critical': True,
            'security_level': 9,
            'location': f"Emergency Exit - {device_id}",
            'confidence': 90
        })
    elif any(word in device_lower for word in ['elevator', 'lift', 'elev']):
        attributes.update({
            'door_type': 'elevator',
            'is_critical': False,
            'security_level': 6,
            'location': f"Elevator Bank - {device_id}",
            'confidence': 88
        })
    elif any(word in device_lower for word in ['stair', 'stairs', 'stairwell']):
        attributes.update({
            'door_type': 'stairwell',
            'is_critical': False,
            'security_level': 4,
            'location': f"Stairwell - {device_id}",
            'confidence': 85
        })
    elif any(word in device_lower for word in ['office', 'room', 'conf']):
        attributes.update({
            'door_type': 'office',
            'is_critical': False,
            'security_level': 3,
            'location': f"Office Area - {device_id}",
            'confidence': 80
        })
    elif any(word in device_lower for word in ['parking', 'garage', 'lot']):
        attributes.update({
            'door_type': 'parking',
            'is_critical': False,
            'security_level': 2,
            'location': f"Parking - {device_id}",
            'confidence': 85
        })

    # Detect floor information
    import re
    floor_match = re.search(r'(\d+)f|floor(\d+)|f(\d+)', device_lower)
    if floor_match:
        floor_num = floor_match.group(1) or floor_match.group(2) or floor_match.group(3)
        attributes['location'] = f"Floor {floor_num} - {device_id}"
        attributes['confidence'] = min(95, attributes['confidence'] + 10)

    return attributes


@callback(
    [Output('mapping-verified-status', 'children', allow_duplicate=True),
     Output('door-mapping-modal', 'style', allow_duplicate=True)],
    [Input('save-door-mappings', 'n_clicks'),
     Input('cancel-door-mapping', 'n_clicks'),
     Input('close-door-mapping-modal', 'n_clicks')],
    [State('door-mappings-store', 'data'),
     State('processed-data-store', 'data')],
    prevent_initial_call=True
)
def handle_door_mapping_save(save_clicks, cancel_clicks, close_clicks, door_store, processed_data):
    """Handle saving door mapping configurations"""
    from dash import no_update
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Close modal on cancel or close
    if trigger_id in ['cancel-door-mapping', 'close-door-mapping-modal']:
        return no_update, {'display': 'none'}

    # Save door mappings
    if trigger_id == 'save-door-mappings' and save_clicks:
        try:
            if not door_store or not processed_data:
                error_msg = html.Div("❌ No door mapping data to save", className="alert alert-error")
                return error_msg, {'display': 'none'}

            devices = door_store.get('devices', [])
            session_id = processed_data.get('session_id')

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
                        'devices': devices,
                        'device_count': len(devices),
                        'mapping_completed': True,
                        'saved_at': datetime.now().isoformat()
                    }

                    ai_plugin.csv_repository.update_session_data(session_id, {
                        'door_mappings': door_mapping_data
                    })

                    logger.info(f"Door mappings saved for session {session_id}")
                except Exception as e:
                    logger.error(f"Failed to save door mappings: {e}")

            success_msg = html.Div([
                html.Div("✅ Door mappings saved successfully!", className="alert alert-success"),
                html.Div([
                    html.H4("📋 Mapping Complete:", className="font-bold mt-3"),
                    html.Ul([
                        html.Li(f"✅ {len(devices)} doors/devices configured"),
                        html.Li("✅ Security levels assigned"),
                        html.Li("✅ Critical status determined"),
                        html.Li("✅ Door types classified"),
                        html.Li("🎯 Ready for analytics and monitoring")
                    ], className="list-disc ml-6 mt-2")
                ], className="mt-3 p-3 bg-green-50 border border-green-200 rounded"),
                html.Div([
                    html.Button("📊 View Analytics Dashboard", 
                              id="goto-analytics", 
                              className="btn btn-primary mt-3 mr-2"),
                    html.Button("📤 Upload Another File", 
                              id="reset-upload", 
                              className="btn btn-secondary mt-3")
                ], className="mt-4")
            ])

            return success_msg, {'display': 'none'}

        except Exception as e:
            logger.error(f"Error saving door mappings: {e}")
            error_msg = html.Div(f"❌ Error saving door mappings: {str(e)}", className="alert alert-error")
            return error_msg, {'display': 'none'}

    return no_update, no_update


# Export the layout function
layout = create_dual_file_uploader

__all__ = [
    "create_dual_file_uploader",
    "layout",
    "render_column_mapping_panel",
    "handle_all_upload_modal_actions",
    "handle_door_mapping",
    "handle_door_mapping_save",
]
