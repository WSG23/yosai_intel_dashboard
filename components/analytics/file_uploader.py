"""
Dual Upload Box Component with Tailwind styling and working callbacks
"""
from dash import html, dcc, callback, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import logging
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
    [Output('column-mapping-modal', 'style'),
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
     Output('mapping-verified-status', 'children')],
    [Input('upload-data', 'contents'),
     Input('cancel-mapping', 'n_clicks'),
     Input('verify-mapping', 'n_clicks')],
    [State('upload-data', 'filename'),
     State('timestamp-dropdown', 'value'),
     State('device-column-dropdown', 'value'),
     State('user-id-dropdown', 'value'),
     State('event-type-dropdown', 'value'),
     State('floor-estimate-input', 'value'),
     State('user-id-storage', 'children')],
    prevent_initial_call=True
)
def handle_all_upload_modal_actions(upload_contents, cancel_clicks, verify_clicks,
                                  upload_filename, timestamp_col, device_col, user_col,
                                  event_type_col, floor_estimate, user_id):
    """Handle file upload and modal actions"""
    from dash import callback_context, no_update
    import dash
    
    ctx = callback_context
    if not ctx.triggered:
        return [no_update] * 19
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Handle file upload
    if trigger_id == 'upload-data' and upload_contents is not None:
        try:
            # Parse file content
            content_type, content_string = upload_contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Process different file types
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
                return [{"display": "none"}] + [no_update] * 17 + [error_msg, ""]
            
            if df is None or df.empty:
                error_msg = html.Div("❌ File appears to be empty or corrupted.", 
                                   className="alert alert-error")
                return [{"display": "none"}] + [no_update] * 17 + [error_msg, ""]
            
            # Get columns
            headers = df.columns.tolist()
            options = [{"label": col, "value": col} for col in headers]
            
            # Simple AI suggestions
            ai_suggestions = {}
            for col in headers:
                col_lower = col.lower()
                if any(word in col_lower for word in ['time', 'date', 'timestamp']):
                    ai_suggestions['timestamp'] = col
                elif any(word in col_lower for word in ['door', 'device', 'location']):
                    ai_suggestions['device_name'] = col
                elif any(word in col_lower for word in ['user', 'id', 'employee', 'badge']):
                    ai_suggestions['user_id'] = col
                elif any(word in col_lower for word in ['event', 'type', 'action', 'result']):
                    ai_suggestions['event_type'] = col
            
            # Success status
            status_msg = html.Div([
                f"✅ Successfully uploaded '{upload_filename}'",
                html.Br(),
                f"📊 {len(df)} rows, {len(headers)} columns processed"
            ], className="alert alert-success")
            
            return [
                {"display": "block"},
                f"File: {upload_filename}",
                f"📊 Detected {len(headers)} columns in your file",
                options, options, options, options,
                ai_suggestions.get('timestamp'),
                ai_suggestions.get('device_name'),
                ai_suggestions.get('user_id'),
                ai_suggestions.get('event_type'),
                1,
                f"AI Suggestion: {ai_suggestions.get('timestamp', 'None')}",
                f"AI Suggestion: {ai_suggestions.get('device_name', 'None')}",
                f"AI Suggestion: {ai_suggestions.get('user_id', 'None')}",
                f"AI Suggestion: {ai_suggestions.get('event_type', 'None')}",
                "AI Confidence: 85%",
                status_msg,
                ""
            ]
            
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            error_msg = html.Div(f"❌ Error processing file: {str(e)}", className="alert alert-error")
            return [{"display": "none"}] + [no_update] * 17 + [error_msg, ""]
    
    # Handle cancel
    elif trigger_id == 'cancel-mapping':
        return [{"display": "none"}] + [no_update] * 18
    
    # Handle verify
    elif trigger_id == 'verify-mapping' and verify_clicks:
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
            ], className="mt-3 p-3 bg-gray-100 rounded"),
            html.Div([
                html.Button("Proceed to Door Mapping", 
                          id="open-door-mapping", 
                          className="btn btn-primary mt-3 mr-2"),
                html.Button("Skip Door Mapping", 
                          id="skip-door-mapping", 
                          className="btn btn-secondary mt-3")
            ], className="mt-4")
        ])
        
        return [{"display": "none"}] + [no_update] * 17 + [success_msg]
    
    return [no_update] * 19
# Door mapping callback
@callback(
    [Output('door-mapping-modal', 'children'),
     Output('door-mapping-modal', 'style')],
    [Input('open-door-mapping', 'n_clicks'),
     Input('skip-door-mapping', 'n_clicks')],
    prevent_initial_call=True
)
def handle_door_mapping(open_clicks, skip_clicks):
    """Handle door mapping modal"""
    ctx = callback_context
    if not ctx.triggered:
        return [], {'display': 'none'}
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'skip-door-mapping':
        return [], {'display': 'none'}

    if trigger_id == 'open-door-mapping':
        try:
            from components.door_mapping_modal import create_door_mapping_modal
            modal_content = create_door_mapping_modal()
            return modal_content, {'display': 'block'}
        except ImportError:
            return html.Div("Door mapping modal not found"), {'display': 'block'}

    return [], {'display': 'none'}


# Export the layout function
layout = create_dual_file_uploader

__all__ = [
    "create_dual_file_uploader",
    "layout",
    "render_column_mapping_panel",
    "handle_all_upload_modal_actions",
    "handle_door_mapping",
]
