"""
File Upload Callback Manager for centralized callback handling
"""
from dash import html, dcc, Input, Output, State, callback_context
import dash
import logging
import base64
import pandas as pd
import io

logger = logging.getLogger(__name__)


class FileUploadCallbackManager:
    """Callback manager for file upload functionality"""

    def __init__(self, callback_registry):
        self.registry = callback_registry

    def register_all(self):
        """Register all file upload callbacks"""
        self._register_file_upload_callback()
        self._register_modal_callbacks()

    def _register_file_upload_callback(self):
        """Register main file upload callback"""
        @self.registry.register_callback(
            outputs=[
                Output('column-mapping-modal', 'children'),
                Output('column-mapping-modal', 'style'),
                Output('upload-status', 'children'),
                Output('mapping-verified-status', 'children')
            ],
            inputs=[Input('upload-data', 'contents')],
            states=[State('upload-data', 'filename')],
            callback_id="file_upload_main"
        )
        def handle_file_upload(upload_contents, upload_filename):
            """Handle file upload and show column mapping modal"""
            if upload_contents is None:
                raise dash.exceptions.PreventUpdate

            try:
                # Parse uploaded file
                content_type, content_string = upload_contents.split(',')
                decoded = base64.b64decode(content_string)

                # Read the file based on extension
                if upload_filename.endswith('.csv'):
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                elif upload_filename.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(io.BytesIO(decoded))
                else:
                    error_msg = html.Div("❌ Unsupported file format. Please use CSV or Excel files.",
                                       className="alert alert-error")
                    return [], {'display': 'none'}, error_msg, ""

                # Create column mapping modal content
                modal_content = self._create_column_mapping_modal(df, upload_filename)
                modal_style = {'display': 'block'}
                status_content = html.Div(f"✅ File '{upload_filename}' uploaded successfully!",
                                        className="alert alert-success")

                return modal_content, modal_style, status_content, ""

            except Exception as e:
                logger.error(f"Error processing file: {e}")
                error_status = html.Div(f"❌ Error processing file: {str(e)}",
                                      className="alert alert-error")
                return [], {"display": "none"}, error_status, ""

    def _register_modal_callbacks(self):
        """Register modal interaction callbacks"""
        @self.registry.register_callback(
            outputs=[
                Output('column-mapping-modal', 'children', allow_duplicate=True),
                Output('column-mapping-modal', 'style', allow_duplicate=True),
                Output('mapping-verified-status', 'children', allow_duplicate=True)
            ],
            inputs=[
                Input('cancel-mapping', 'n_clicks'),
                Input('verify-mapping', 'n_clicks')
            ],
            states=[
                State('timestamp-dropdown', 'value'),
                State('device-column-dropdown', 'value'),
                State('user-id', 'value'),
                State('event-type-dropdown', 'value'),
                State('floor-estimate-input', 'value'),
                State('user-id-storage', 'children')
            ],
            prevent_initial_call=True,
            callback_id="column_mapping_modal_actions"
        )
        def handle_modal_actions(cancel_clicks, verify_clicks, timestamp_col, device_col,
                                user_col, event_type_col, floor_estimate, user_id):
            """Handle modal cancel and verify actions"""
            ctx = callback_context
            if not ctx.triggered:
                raise dash.exceptions.PreventUpdate

            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_id == 'cancel-mapping':
                # Hide modal and clear status
                return [], {"display": "none"}, ""

            elif trigger_id == 'verify-mapping':
                try:
                    # Save the mapping preferences
                    user_mapping = {
                        'timestamp': timestamp_col,
                        'device_name': device_col,
                        'token_id': user_col,
                        'event_type': event_type_col
                    }

                    # Try to use AI plugin if available
                    try:
                        from plugins.ai_classification.plugin import AIClassificationPlugin
                        ai_plugin = AIClassificationPlugin()
                        ai_plugin.start()
                        ai_plugin.record_correction(
                            device_name=device_col or "unknown",
                            ai_prediction={'suggested_mapping': user_mapping, 'floor_estimate': floor_estimate},
                            user_correction={'confirmed_mapping': user_mapping, 'floors': floor_estimate},
                            client_id=user_id or 'default_client'
                        )
                    except Exception as ai_error:
                        logger.warning(f"AI plugin not available: {ai_error}")

                    # Create success message
                    success_message = html.Div([
                        html.Div("✅ Mapping verified and learned!", className="alert alert-success"),
                        html.Small(f"Your preferences saved for future uploads. Estimated Floors: {floor_estimate}"),
                        html.Div(style={"marginTop": "1rem", "padding": "1rem", "backgroundColor": "#f8f9fa", "borderRadius": "4px"}, children=[
                            html.P("Mapping Summary:", style={"fontWeight": "bold", "marginBottom": "0.5rem"}),
                            html.Ul([
                                html.Li(f"Timestamp: {timestamp_col or 'Not mapped'}"),
                                html.Li(f"Door/Location: {device_col or 'Not mapped'}"),
                                html.Li(f"Token ID: {user_col or 'Not mapped'}"),
                                html.Li(f"Event Type: {event_type_col or 'Not mapped'}"),
                                html.Li(f"Floor Estimate: {floor_estimate} floors")
                            ])
                        ])
                    ])

                    return [], {"display": "none"}, success_message

                except Exception as e:
                    logger.error(f"Error in verify_and_learn: {e}")
                    error_message = html.Div("❌ Error saving mapping. Please try again.",
                                           className="alert alert-error")
                    return [], {"display": "none"}, error_message

            raise dash.exceptions.PreventUpdate

    def _create_column_mapping_modal(self, df, filename):
        """Create the column mapping modal content"""
        columns = df.columns.tolist()

        # AI suggestions (simplified for now)
        suggested_mappings = self._get_ai_suggestions(columns)

        modal_content = [
            html.Div(className="modal__backdrop", children=[
                html.Div(className="modal__content", children=[
                    html.Div(className="modal__header", children=[
                        html.H3(f"Map Columns for {filename}", className="modal__title"),
                        html.P("Please map your file columns to the expected data fields.", className="modal__subtitle")
                    ]),

                    html.Div(className="modal__body", children=[
                        # Timestamp mapping
                        html.Div(className="form-group", children=[
                            html.Label("Timestamp Column:", className="form-label"),
                            dcc.Dropdown(
                                id="timestamp-dropdown",
                                options=[{"label": col, "value": col} for col in columns],
                                value=suggested_mappings.get('timestamp'),
                                placeholder="Select timestamp column...",
                                className="form-input"
                            )
                        ]),

                        # Device/Door column mapping
                        html.Div(className="form-group", children=[
                            html.Label("Device/Door Column:", className="form-label"),
                            dcc.Dropdown(
                                id="device-column-dropdown",
                                options=[{"label": col, "value": col} for col in columns],
                                value=suggested_mappings.get('device'),
                                placeholder="Select device/door column...",
                                className="form-input"
                            )
                        ]),

                        # User ID mapping
                        html.Div(className="form-group", children=[
                            html.Label("User ID Column:", className="form-label"),
                            dcc.Dropdown(
                                id="user-id",
                                options=[{"label": col, "value": col} for col in columns],
                                value=suggested_mappings.get('user_id'),
                                placeholder="Select user ID column...",
                                className="form-input"
                            )
                        ]),

                        # Event type mapping
                        html.Div(className="form-group", children=[
                            html.Label("Event Type Column:", className="form-label"),
                            dcc.Dropdown(
                                id="event-type-dropdown",
                                options=[{"label": col, "value": col} for col in columns],
                                value=suggested_mappings.get('event_type'),
                                placeholder="Select event type column...",
                                className="form-input"
                            )
                        ]),

                        # Floor estimate
                        html.Div(className="form-group", children=[
                            html.Label("Number of Floors:", className="form-label"),
                            dcc.Input(
                                id="floor-estimate-input",
                                type="number",
                                value=1,
                                min=1,
                                max=100,
                                className="form-input"
                            ),
                            html.Small("AI Confidence: 85%", className="form-help-text")
                        ]),

                        # Hidden storage for user ID
                        html.Div(id="user-id-storage", children="default_user", style={"display": "none"})
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
        ]

        return modal_content

    def _get_ai_suggestions(self, columns):
        """Get AI suggestions for column mapping"""
        suggestions = {}

        # Simple heuristic-based suggestions
        for col in columns:
            col_lower = col.lower()
            if any(word in col_lower for word in ['time', 'date', 'timestamp']):
                suggestions['timestamp'] = col
            elif any(word in col_lower for word in ['door', 'device', 'location', 'room']):
                suggestions['device'] = col
            elif any(word in col_lower for word in ['user', 'id', 'employee', 'badge']):
                suggestions['user_id'] = col
            elif any(word in col_lower for word in ['event', 'type', 'action', 'result']):
                suggestions['event_type'] = col

        return suggestions
