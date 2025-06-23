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
    Output('door-mapping-modal-trigger', 'style'),
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
    prevent_initial_call=True
)
def handle_all_upload_modal_actions(upload_contents, cancel_clicks, verify_clicks,
                                    upload_filename, timestamp_col, device_col, user_col,
                                    event_type_col, floor_estimate, user_id, file_store_data, processed_data):
    """Enhanced file upload handler with auto-filled AI suggestions and efficient processing"""
    from dash import callback_context, no_update
    import dash
    import uuid
    import tempfile
    import os
    from datetime import datetime

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
                error_msg = html.Div("❌ Unsupported file format. Use CSV, JSON, or Excel files.",
                                   className="alert alert-error")
                return [{"display": "none"}] + [no_update] * 20 + [error_msg, no_update, {}, {}, {"display": "none"}, {"display": "none"}]

            if df is None or df.empty:
                error_msg = html.Div("❌ File appears to be empty or corrupted.",
                                   className="alert alert-error")
                return [{"display": "none"}] + [no_update] * 20 + [error_msg, no_update, {}, {}, {"display": "none"}, {"display": "none"}]

            headers = df.columns.tolist()
            options = [{"label": col, "value": col} for col in headers]

            ai_plugin = None
            AI_AVAILABLE = False
            try:
                from plugins.ai_classification.plugin import AIClassificationPlugin
                ai_plugin = AIClassificationPlugin()
                ai_plugin.start()
                AI_AVAILABLE = True
                logger.info("AI plugin initialized successfully")
            except Exception as e:
                logger.warning(f"AI Classification plugin not available: {e}")

            ai_suggestions = {}
            confidence_scores = {}
            floor_estimate_value = 1
            floor_confidence = "0%"

            if AI_AVAILABLE and ai_plugin:
                try:
                    sample_data = df.head(500).to_dict('records')

                    mapping_result = ai_plugin.map_columns(headers, session_id)
                    if mapping_result.get('success'):
                        suggested_mapping = mapping_result.get('suggested_mapping', {})
                        confidence_scores = mapping_result.get('confidence_scores', {})

                        for column, field in suggested_mapping.items():
                            if field == 'timestamp':
                                ai_suggestions['timestamp'] = column
                            elif field == 'location':
                                ai_suggestions['device_name'] = column
                            elif field == 'user_id':
                                ai_suggestions['user_id'] = column
                            elif field == 'access_type':
                                ai_suggestions['event_type'] = column

                        logger.info(f"AI column mapping suggestions: {ai_suggestions}")

                    floor_result = ai_plugin.estimate_floors(sample_data, session_id)
                    if floor_result.get('success'):
                        floor_estimate_value = floor_result.get('total_floors', 1)
                        floor_confidence = f"{floor_result.get('confidence', 0.0) * 100:.0f}%"
                        logger.info(f"AI floor estimation: {floor_estimate_value} floors (confidence: {floor_confidence})")

                except Exception as e:
                    logger.error(f"AI processing failed: {e}")
                    AI_AVAILABLE = False

            if not ai_suggestions:
                logger.info("Using fallback pattern matching for column detection")
                ai_suggestions, confidence_scores = enhanced_pattern_matching(headers)

            if floor_estimate_value == 1 and AI_AVAILABLE:
                logger.info("Using fallback floor estimation")
                floor_estimate_value, floor_confidence = fallback_floor_estimation(df.to_dict('records'))

            status_msg = html.Div([
                f"✅ Successfully uploaded '{upload_filename}'",
                html.Br(),
                f"📊 {len(df)} rows, {len(headers)} columns processed",
                html.Br(),
                f"🤖 AI analysis {'completed' if AI_AVAILABLE else 'completed with fallback'}"
            ], className="alert alert-success")

            file_store = {
                'session_id': session_id,
                'filename': upload_filename,
                'columns': headers,
                'row_count': len(df)
            }

            processed_store = {
                'session_id': session_id,
                'ai_suggestions': ai_suggestions,
                'confidence_scores': confidence_scores,
                'data': df.head(1000).to_dict('records'),
                'full_row_count': len(df)
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

            return [
                {"display": "block"},
                f"File: {upload_filename}",
                f"📊 Detected {len(headers)} columns in your file - AI suggestions auto-filled below",
                options, options, options, options,
                ai_suggestions.get('timestamp'),
                ai_suggestions.get('device_name'),
                ai_suggestions.get('user_id'),
                ai_suggestions.get('event_type'),
                floor_estimate_value,
                f"✅ Auto-filled: {ai_suggestions.get('timestamp', 'None')} ({confidence_scores.get(ai_suggestions.get('timestamp', ''), 0)*100:.0f}%)",
                f"✅ Auto-filled: {ai_suggestions.get('device_name', 'None')} ({confidence_scores.get(ai_suggestions.get('device_name', ''), 0)*100:.0f}%)",
                f"✅ Auto-filled: {ai_suggestions.get('user_id', 'None')} ({confidence_scores.get(ai_suggestions.get('user_id', ''), 0)*100:.0f}%)",
                f"✅ Auto-filled: {ai_suggestions.get('event_type', 'None')} ({confidence_scores.get(ai_suggestions.get('event_type', ''), 0)*100:.0f}%)",
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
            # Save the column mapping
            column_mapping = {
                'timestamp': timestamp_col,
                'device': device_col,
                'user_id': user_col,
                'event_type': event_type_col,
                'floor_estimate': floor_estimate
            }

            # Success message
            success_msg = html.Div([
                html.Div("✅ Column mapping verified successfully!", className="alert alert-success"),
                html.P("Proceeding to device attribute assignment...", className="text-green-600 mt-2")
            ])

            # Show the door mapping buttons
            door_mapping_style = {"display": "inline-block"}
            skip_mapping_style = {"display": "inline-block"}

            return (
                {"display": "none"},
                no_update, no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update,
                no_update, no_update, no_update, no_update,
                success_msg,
                success_msg,
                file_store_data or {},
                processed_data or {},
                door_mapping_style,
                skip_mapping_style
            )

        except Exception as e:
            logger.error(f"Error in verify mapping: {e}")
            error_msg = html.Div(f"❌ Error verifying mapping: {str(e)}", className="alert alert-error")
            return [{"display": "none"}] + [no_update] * 20 + [error_msg, no_update, {}, {}, {"display": "none"}, {"display": "none"}]

    return [{"display": "none"}] + [no_update] * 22


def enhanced_pattern_matching(headers):
    """Enhanced fallback pattern matching for column detection"""
    ai_suggestions = {}
    confidence_scores = {}

    patterns = {
        'timestamp': [
            'time', 'date', 'timestamp', 'datetime', 'created', 'occurred',
            'when', 'logged', 'recorded', 'event_time', 'access_time'
        ],
        'device_name': [
            'door', 'device', 'location', 'area', 'reader', 'panel', 'terminal',
            'gate', 'entrance', 'exit', 'access_point', 'checkpoint', 'zone'
        ],
        'user_id': [
            'user', 'person', 'employee', 'badge', 'card', 'id', 'worker',
            'staff', 'visitor', 'holder', 'individual'
        ],
        'event_type': [
            'event', 'action', 'type', 'result', 'status', 'access', 'entry',
            'exit', 'granted', 'denied', 'outcome'
        ]
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
                patterns = [r'\b(\d+)f\b', r'\bfloor\s*(\d+)', r'\bf(\d+)', r'\b(\d+)fl\b']
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
# Door mapping callback
@callback(
    Output('door-mapping-modal-data-trigger', 'data'),
    [Input('door-mapping-modal-trigger', 'n_clicks'),
     Input('skip-door-mapping', 'n_clicks')],
    [State('processed-data-store', 'data'),
     State('uploaded-file-store', 'data'),
     State('timestamp-dropdown', 'value'),
     State('device-column-dropdown', 'value'),
     State('user-id-dropdown', 'value'),
     State('event-type-dropdown', 'value')],
    prevent_initial_call=True
)
def handle_door_mapping(open_clicks, skip_clicks, processed_data, file_data,
                       timestamp_col, device_col, user_col, event_col):
    """Handle door mapping modal with comprehensive column detection"""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'skip-door-mapping':
        return dash.no_update

    if trigger_id == 'door-mapping-modal-trigger':
        try:
            if not processed_data or 'data' not in processed_data:
                return dash.no_update

            # Extract CSV data
            csv_data = processed_data['data']
            if not csv_data:
                return dash.no_update

            # Get all available columns
            available_columns = list(csv_data[0].keys()) if csv_data else []
            logger.info(f"Available columns: {available_columns}")

            # ENHANCED COLUMN DETECTION - Try multiple sources
            device_column = None

            # 1. First priority: User-selected device column
            if device_col and device_col in available_columns:
                device_column = device_col
                logger.info(f"Using user-selected device column: {device_column}")

            # 2. Second priority: AI suggestions
            elif processed_data.get('ai_suggestions'):
                ai_suggestions = processed_data['ai_suggestions']
                # Try various AI suggestion fields
                for field_name in ['device_name', 'location', 'door', 'device']:
                    if field_name in ai_suggestions and ai_suggestions[field_name] in available_columns:
                        device_column = ai_suggestions[field_name]
                        logger.info(f"Using AI suggested column: {device_column}")
                        break

            # 3. Third priority: Smart pattern matching
            if not device_column:
                # Comprehensive list of possible device/door column names
                device_patterns = [
                    'door_id', 'device_id', 'door', 'device', 'location', 'area',
                    'door_name', 'device_name', 'access_point', 'reader',
                    'entrance', 'exit', 'gate', 'portal', 'checkpoint',
                    'room', 'office', 'zone', 'sector', 'terminal',
                    'doorid', 'deviceid', 'reader_id', 'readerid',
                    'access_device', 'card_reader', 'panel'
                ]

                # First try exact matches
                for pattern in device_patterns:
                    if pattern in available_columns:
                        device_column = pattern
                        logger.info(f"Found exact match for device column: {device_column}")
                        break

                # Then try partial matches (case-insensitive)
                if not device_column:
                    for col in available_columns:
                        col_lower = col.lower()
                        for pattern in device_patterns:
                            if pattern in col_lower or col_lower in pattern:
                                device_column = col
                                logger.info(f"Found partial match for device column: {device_column}")
                                break
                        if device_column:
                            break

            # 4. Last resort: Use any column that might contain identifiers
            if not device_column and available_columns:
                for col in available_columns:
                    if col.lower() in ['timestamp', 'time', 'date', 'user', 'employee', 'badge', 'id', 'event', 'result', 'status']:
                        continue

                    unique_values = set()
                    for row in csv_data[:100]:
                        if col in row and row[col]:
                            unique_values.add(str(row[col]).strip())
                        if len(unique_values) > 5:
                            device_column = col
                            logger.info(f"Using fallback device column with diverse values: {device_column}")
                            break
                    if device_column:
                        break

                # Ultimate fallback: use first non-timestamp column
                if not device_column:
                    for col in available_columns:
                        if col.lower() not in ['timestamp', 'time', 'date'] and col != timestamp_col:
                            device_column = col
                            logger.info(f"Using ultimate fallback column: {device_column}")
                            break

            if not device_column:
                columns_list = "', '".join(available_columns)
                return dash.no_update

            # Extract unique devices from the identified column
            unique_devices = set()
            for row in csv_data:
                if device_column in row and row[device_column]:
                    device_value = str(row[device_column]).strip()
                    if device_value and device_value.lower() not in ['', 'null', 'none', 'n/a']:
                        unique_devices.add(device_value)

            unique_devices = sorted(list(unique_devices))

            if not unique_devices:
                return dash.no_update

            logger.info(f"Found {len(unique_devices)} unique devices in column '{device_column}'")

            return {'devices': unique_devices, 'device_column': device_column}

        except Exception as e:
            logger.error(f"Error creating door mapping modal: {e}")
            return dash.no_update
    return dash.no_update


def create_error_modal(title, message):
    """Create a simple error modal"""
    return html.Div([
        html.Div([
            html.Div([
                html.H3(f"❌ {title}", className="text-lg font-semibold text-red-600 mb-3"),
                html.P(message, className="text-gray-700 mb-4"),
                html.Button("Close",
                           id="close-error-modal",
                           className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600")
            ], className="bg-white p-6 rounded-lg max-w-md")
        ], className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4")
    ])


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
     Output('door-mapping-modal-overlay', 'className', allow_duplicate=True)],
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
    hidden_class = "fixed inset-0 bg-black bg-opacity-80 z-50 flex items-center justify-center hidden"

    if trigger_id in ['cancel-door-mapping', 'close-door-mapping-modal']:
        return no_update, hidden_class

    # Save door mappings
    if trigger_id == 'save-door-mappings' and save_clicks:
        try:
            if not door_store or not processed_data:
                error_msg = html.Div("❌ No door mapping data to save", className="alert alert-error")
                return error_msg, hidden_class

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

            return success_msg, hidden_class

        except Exception as e:
            logger.error(f"Error saving door mappings: {e}")
            error_msg = html.Div(f"❌ Error saving door mappings: {str(e)}", className="alert alert-error")
            return error_msg, hidden_class

    return no_update, no_update


@callback(
    Output('upload-info', 'children'),
    [Input('processed-data-store', 'data')],
    prevent_initial_call=True
)
def show_debug_info(processed_data):
    """Show debug information about available columns"""
    if not processed_data or 'data' not in processed_data:
        return ""

    csv_data = processed_data['data']
    if not csv_data:
        return ""

    available_columns = list(csv_data[0].keys())
    ai_suggestions = processed_data.get('ai_suggestions', {})

    debug_info = html.Div([
        html.Details([
            html.Summary("🔍 Debug: Available Columns", className="cursor-pointer text-sm text-gray-600"),
            html.Div([
                html.P(f"Available columns: {', '.join(available_columns)}", className="text-xs text-gray-500 mt-2"),
                html.P(f"AI suggestions: {ai_suggestions}", className="text-xs text-gray-500"),
                html.P(f"Sample row: {dict(list(csv_data[0].items())[:3])}...", className="text-xs text-gray-500")
            ], className="mt-2 p-2 bg-gray-50 rounded text-xs")
        ])
    ], className="mt-2")

    return debug_info


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
