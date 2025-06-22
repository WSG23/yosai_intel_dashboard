"""
Comprehensive File Upload Callback Manager
Handles the complete workflow: Upload → Column Mapping → Door Mapping
"""
from dash import html, dcc, Input, Output, State, callback_context
import dash
import logging
import base64
import pandas as pd
import io
import json

logger = logging.getLogger(__name__)


class FileUploadCallbackManager:
    """Complete callback manager for file upload workflow"""

    def __init__(self, callback_registry):
        self.registry = callback_registry

    def register_all(self):
        """Register all file upload workflow callbacks"""
        self._register_file_upload_callback()
        self._register_column_mapping_callbacks()
        self._register_door_mapping_trigger()
        self._register_upload_feedback_callbacks()

    def _register_file_upload_callback(self):
        """Register main file upload processing callback"""
        @self.registry.register_callback(
            outputs=[
                Output('upload-status', 'children'),
                Output('upload-info', 'children'),
                Output('column-mapping-modal', 'children'),
                Output('column-mapping-modal', 'style'),
                Output('uploaded-file-store', 'data')
            ],
            inputs=[Input('upload-data', 'contents')],
            states=[State('upload-data', 'filename')],
            callback_id="main_file_upload_processing"
        )
        def handle_file_upload(contents, filename):
            """Process uploaded file and show column mapping"""
            if contents is None:
                raise dash.exceptions.PreventUpdate

            try:
                # Parse file content
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)

                # Process different file types
                df = None
                if filename.endswith('.csv'):
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                elif filename.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(io.BytesIO(decoded))
                elif filename.endswith('.json'):
                    # Handle JSON files
                    json_data = json.loads(decoded.decode('utf-8'))
                    if isinstance(json_data, list):
                        df = pd.DataFrame(json_data)
                    else:
                        df = pd.json_normalize(json_data)
                else:
                    error_msg = html.Div([
                        "❌ Unsupported file format.",
                        html.Br(),
                        "Supported formats: CSV (.csv), JSON (.json), Excel (.xlsx, .xls)"
                    ], className="alert alert-error")
                    return error_msg, "", [], {'display': 'none'}, {}

                if df is None or df.empty:
                    error_msg = html.Div("❌ File appears to be empty or corrupted.",
                                       className="alert alert-error")
                    return error_msg, "", [], {'display': 'none'}, {}

                # Create file info display
                file_info = self._create_file_info_display(df, filename)

                # Create column mapping modal
                modal_content = self._create_column_mapping_modal(df, filename)
                modal_style = {'display': 'block', 'position': 'fixed', 'top': '0', 'left': '0',
                               'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.8)',
                               'zIndex': '1000'}

                # Success status
                success_msg = html.Div([
                    f"✅ Successfully uploaded '{filename}'",
                    html.Br(),
                    f"📊 Found {len(df)} rows and {len(df.columns)} columns"
                ], className="alert alert-success")

                # Store file data for next steps
                file_data = {
                    'filename': filename,
                    'data': df.to_dict('records'),
                    'columns': df.columns.tolist()
                }

                return success_msg, file_info, modal_content, modal_style, file_data

            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                error_msg = html.Div([
                    f"❌ Error processing file: {str(e)}",
                    html.Br(),
                    "Please check file format and try again."
                ], className="alert alert-error")
                return error_msg, "", [], {'display': 'none'}, {}

    def _register_column_mapping_callbacks(self):
        """Register column mapping modal callbacks"""
        @self.registry.register_callback(
            outputs=[
                Output('column-mapping-modal', 'style', allow_duplicate=True),
                Output('mapping-verified-status', 'children'),
                Output('processed-data-store', 'data'),
                Output('door-mapping-modal-data-trigger', 'data')
            ],
            inputs=[
                Input('cancel-mapping', 'n_clicks'),
                Input('verify-mapping', 'n_clicks')
            ],
            states=[
                State('timestamp-dropdown', 'value'),
                State('device-column-dropdown', 'value'),
                State('user-id-dropdown', 'value'),
                State('event-type-dropdown', 'value'),
                State('floor-estimate-input', 'value'),
                State('uploaded-file-store', 'data'),
                State('user-id-storage', 'children')
            ],
            prevent_initial_call=True,
            callback_id="column_mapping_modal_actions"
        )
        def handle_column_mapping_actions(cancel_clicks, verify_clicks, timestamp_col,
                                         device_col, user_col, event_type_col, floor_estimate,
                                         file_data, user_id):
            """Handle column mapping modal actions"""
            ctx = callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_id == 'cancel-mapping':
                # Hide modal and clear status
                return {'display': 'none'}, "", {}, {}

            elif trigger_id == 'verify-mapping':
                try:
                    # Validate mapping
                    if not any([timestamp_col, device_col, user_col, event_type_col]):
                        error_msg = html.Div(
                            "❌ Please map at least one column before proceeding.",
                            className="alert alert-warning")
                        return dash.no_update, error_msg, {}, {}

                    # Create mapping configuration
                    mapping_config = {
                        'timestamp': timestamp_col,
                        'device_name': device_col,
                        'user_id': user_col,
                        'event_type': event_type_col,
                        'floor_estimate': floor_estimate or 1
                    }

                    # Save AI learning data
                    try:
                        from plugins.ai_classification.plugin import AIClassificationPlugin
                        ai_plugin = AIClassificationPlugin()
                        ai_plugin.start()
                        ai_plugin.record_correction(
                            device_name=device_col or "unknown",
                            ai_prediction={'suggested_mapping': mapping_config},
                            user_correction={'confirmed_mapping': mapping_config},
                            client_id=user_id or 'default_client'
                        )
                    except Exception as ai_error:
                        logger.warning(f"AI plugin not available: {ai_error}")

                    # Prepare data for door mapping
                    if file_data and 'data' in file_data:
                        processed_data = {
                            'filename': file_data.get('filename'),
                            'mapping': mapping_config,
                            'data': file_data['data']
                        }

                        # Trigger door mapping modal
                        door_mapping_data = {
                            'devices': self._extract_devices_for_mapping(file_data['data'], mapping_config)
                        }
                    else:
                        processed_data = {}
                        door_mapping_data = {}

                    # Create success message
                    success_msg = html.Div([
                        html.Div("✅ Column mapping verified successfully!", className="alert alert-success"),
                        html.Div([
                            html.H4("Mapping Summary:", className="font-bold mt-3"),
                            html.Ul([
                                html.Li(f"Timestamp: {timestamp_col or 'Not mapped'}"),
                                html.Li(f"Device/Door: {device_col or 'Not mapped'}"),
                                html.Li(f"User ID: {user_col or 'Not mapped'}"),
                                html.Li(f"Event Type: {event_type_col or 'Not mapped'}"),
                                html.Li(f"Floor Estimate: {floor_estimate or 1} floors")
                            ], className="list-disc ml-6 mt-2")
                        ], className="mt-3 p-3 bg-gray-100 rounded"),
                        html.Div([
                            html.Button("Proceed to Door Mapping",
                                        id="open-door-mapping",
                                        className="btn btn-primary mt-3 mr-2"),
                            html.Button("Skip Door Mapping",
                                        id="skip-door-mapping",
                                        className="btn btn-secondary mt-3")
                        ])
                    ])

                    return {'display': 'none'}, success_msg, processed_data, door_mapping_data

                except Exception as e:
                    logger.error(f"Error in column mapping verification: {e}")
                    error_msg = html.Div(f"❌ Error saving mapping: {str(e)}",
                                       className="alert alert-error")
                    return dash.no_update, error_msg, {}, {}

            raise dash.exceptions.PreventUpdate

    def _register_door_mapping_trigger(self):
        """Register door mapping modal trigger"""
        @self.registry.register_callback(
            outputs=[
                Output('door-mapping-modal', 'children'),
                Output('door-mapping-modal', 'style')
            ],
            inputs=[
                Input('open-door-mapping', 'n_clicks'),
                Input('skip-door-mapping', 'n_clicks')
            ],
            prevent_initial_call=True,
            callback_id="door_mapping_trigger"
        )
        def handle_door_mapping_trigger(open_clicks, skip_clicks):
            """Handle door mapping modal trigger"""
            ctx = callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_id == 'skip-door-mapping':
                return [], {'display': 'none'}

            elif trigger_id == 'open-door-mapping':
                try:
                    from components.door_mapping_modal import create_door_mapping_modal
                    modal_content = create_door_mapping_modal()
                    modal_style = {'display': 'block'}
                    return modal_content, modal_style
                except ImportError:
                    error_content = html.Div("Door mapping modal not available",
                                           className="alert alert-warning")
                    return error_content, {'display': 'block'}

            return [], {'display': 'none'}

    def _register_upload_feedback_callbacks(self):
        """Register visual feedback callbacks for upload states"""
        @self.registry.register_clientside_callback(
            """
            function(contents, filename) {
                if (!contents) {
                    return [
                        '/assets/navbar_icons/upload.png',
                        'upload-box upload-box-active'
                    ];
                }
                return [
                    '/assets/navbar_icons/upload.png',
                    'upload-box upload-box-processing'
                ];
            }
            """,
            outputs=[
                Output('upload-data-icon', 'src'),
                Output('upload-data-box', 'className')
            ],
            inputs=[
                Input('upload-data', 'contents'),
                Input('upload-data', 'filename')
            ],
            callback_id="upload_visual_feedback"
        )

    def _create_file_info_display(self, df, filename):
        """Create file information display"""
        return html.Div([
            html.H4(f"📄 File: {filename}", className="font-bold"),
            html.P(f"📊 {len(df)} rows × {len(df.columns)} columns"),
            html.Details([
                html.Summary("📋 Column Names", className="font-semibold cursor-pointer"),
                html.Div([
                    html.Span(col, className="inline-block bg-blue-100 text-blue-800 px-2 py-1 rounded mr-2 mb-1")
                    for col in df.columns.tolist()
                ], className="mt-2")
            ], className="mt-2"),
            html.Details([
                html.Summary("🔍 Data Preview (first 3 rows)", className="font-semibold cursor-pointer"),
                html.Div([
                    html.Table([
                        html.Thead([
                            html.Tr([html.Th(col, className='border px-2 py-1') for col in df.columns])
                        ]),
                        html.Tbody([
                            html.Tr([
                                html.Td(str(df.iloc[i][col]), className='border px-2 py-1')
                                for col in df.columns
                            ]) for i in range(min(3, len(df)))
                        ])
                    ], className="border-collapse border w-full text-sm")
                ], className="mt-2 overflow-x-auto")
            ], className="mt-2")
        ], className="bg-gray-50 p-4 rounded border")

    def _create_column_mapping_modal(self, df, filename):
        """Create comprehensive column mapping modal"""
        columns = df.columns.tolist()
        ai_suggestions = self._get_ai_column_suggestions(columns)

        return [
            html.Div([
                html.Div([
                    # Modal header
                    html.Div([
                        html.H3(f"🎯 Map Columns for {filename}", className="text-xl font-bold text-white"),
                        html.P("Map your file columns to the expected security data fields",
                               className="text-gray-300")
                    ], className="p-6 border-b border-gray-600"),

                    # Modal body
                    html.Div([
                        # AI Suggestions banner
                        html.Div([
                            "🤖 AI has analyzed your columns and provided suggestions below"
                        ], className="bg-blue-600 text-white p-3 rounded mb-4"),

                        # Column mapping form
                        html.Div([
                            # Timestamp mapping
                            html.Div([
                                html.Label("🕒 Timestamp Column:", className="form-label"),
                                dcc.Dropdown(
                                    id="timestamp-dropdown",
                                    options=[{"label": col, "value": col} for col in columns],
                                    value=ai_suggestions.get('timestamp'),
                                    placeholder="Select timestamp column...",
                                    className="form-dropdown"
                                ),
                                html.Small("Maps to when events occurred", className="text-gray-400")
                            ], className="form-group"),

                            # Device column mapping
                            html.Div([
                                html.Label("🚪 Device/Door Column:", className="form-label"),
                                dcc.Dropdown(
                                    id="device-column-dropdown",
                                    options=[{"label": col, "value": col} for col in columns],
                                    value=ai_suggestions.get('device'),
                                    placeholder="Select device/door column...",
                                    className="form-dropdown"
                                ),
                                html.Small("Maps to door/device identifiers", className="text-gray-400")
                            ], className="form-group"),

                            # User ID mapping
                            html.Div([
                                html.Label("👤 User ID Column:", className="form-label"),
                                dcc.Dropdown(
                                    id="user-id-dropdown",
                                    options=[{"label": col, "value": col} for col in columns],
                                    value=ai_suggestions.get('user_id'),
                                    placeholder="Select user ID column...",
                                    className="form-dropdown"
                                ),
                                html.Small("Maps to employee/badge IDs", className="text-gray-400")
                            ], className="form-group"),

                            # Event type mapping
                            html.Div([
                                html.Label("⚡ Event Type Column:", className="form-label"),
                                dcc.Dropdown(
                                    id="event-type-dropdown",
                                    options=[{"label": col, "value": col} for col in columns],
                                    value=ai_suggestions.get('event_type'),
                                    placeholder="Select event type column...",
                                    className="form-dropdown"
                                ),
                                html.Small("Maps to access granted/denied/etc", className="text-gray-400")
                            ], className="form-group"),

                            # Floor estimate
                            html.Div([
                                html.Label("🏛️ Number of Floors:", className="form-label"),
                                dcc.Input(
                                    id="floor-estimate-input",
                                    type="number",
                                    value=ai_suggestions.get('floors', 1),
                                    min=1,
                                    max=100,
                                    className="form-input"
                                ),
                                html.Small(f"AI Confidence: {ai_suggestions.get('confidence', 85)}%",
                                         className="text-blue-400")
                            ], className="form-group")
                        ], className="space-y-4"),

                        # Hidden storage
                        html.Div(id="user-id-storage", children="default_user", style={"display": "none"})

                    ], className="p-6"),

                    # Modal footer
                    html.Div([
                        html.Button("Cancel", id="cancel-mapping",
                                   className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 mr-3"),
                        html.Button("✅ Verify & Learn", id="verify-mapping",
                                   className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 font-bold")
                    ], className="p-6 border-t border-gray-600 flex justify-end")

                ], className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-screen overflow-y-auto")
            ], className="fixed inset-0 flex items-center justify-center p-4")
        ]

    def _get_ai_column_suggestions(self, columns):
        """Generate AI suggestions for column mapping"""
        suggestions = {'confidence': 85}

        for col in columns:
            col_lower = col.lower()

            # Timestamp detection
            if any(word in col_lower for word in ['time', 'date', 'timestamp', 'datetime', 'created', 'occurred']):
                suggestions['timestamp'] = col

            # Device/Door detection
            elif any(word in col_lower for word in ['door', 'device', 'location', 'room', 'gate', 'entry', 'access_point']):
                suggestions['device'] = col

            # User ID detection
            elif any(word in col_lower for word in ['user', 'employee', 'badge', 'card', 'id', 'person', 'token']):
                suggestions['user_id'] = col

            # Event type detection
            elif any(word in col_lower for word in ['event', 'type', 'action', 'result', 'status', 'access', 'granted', 'denied']):
                suggestions['event_type'] = col

        # Estimate floors based on device variety
        suggestions['floors'] = max(1, len(set([col for col in columns if 'floor' in col.lower()])) or 1)

        return suggestions

    def _extract_devices_for_mapping(self, data, mapping_config):
        """Extract unique devices for door mapping"""
        device_col = mapping_config.get('device_name')
        if not device_col or not data:
            return []

        # Extract unique devices
        devices = set()
        for row in data:
            if device_col in row and row[device_col]:
                devices.add(str(row[device_col]))

        # Create device mapping data
        device_list = []
        for i, device in enumerate(sorted(devices)):
            device_list.append({
                'device_id': device,
                'location': f"Location {i+1}",  # Default location
                'critical': False,  # Default not critical
                'security_level': 50  # Default medium security
            })

        return device_list
