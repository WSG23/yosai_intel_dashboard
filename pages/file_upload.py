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
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH, ctx
import dash_bootstrap_components as dbc

from components.column_verification import (
    create_column_verification_modal,
    get_ai_column_suggestions,
    save_verified_mappings,
)

logger = logging.getLogger(__name__)

# Global storage for uploaded data (in production, use database or session storage)
_uploaded_data_store: Dict[str, pd.DataFrame] = {}


def layout():
    """File upload page layout"""
    return dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H1("📁 File Upload", className="text-primary mb-2"),
                html.P(
                    "Upload CSV, Excel, or JSON files for analysis",
                    className="text-muted mb-4"
                ),
            ])
        ]),

        # Upload area
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📤 Upload Data Files", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                html.I(className="fas fa-cloud-upload-alt fa-4x mb-3 text-primary"),
                                html.H5("Drag and Drop or Click to Select Files"),
                                html.P("Supports CSV, Excel (.xlsx, .xls), and JSON files", 
                                      className="text-muted"),
                                html.Small("Maximum file size: 10MB", className="text-secondary")
                            ], className="text-center p-5"),
                            style={
                                'width': '100%',
                                'border': '2px dashed #007bff',
                                'borderRadius': '8px',
                                'textAlign': 'center',
                                'cursor': 'pointer',
                                'backgroundColor': '#f8f9fa'
                            },
                            multiple=True
                        )
                    ])
                ])
            ])
        ], className="mb-4"),

        # Upload status and file list
        dbc.Row([
            dbc.Col([
                html.Div(id='upload-results')
            ])
        ], className="mb-4"),

        # Data preview area
        dbc.Row([
            dbc.Col([
                html.Div(id='file-preview')
            ])
        ]),

        # Navigation to analytics
        dbc.Row([
            dbc.Col([
                html.Div(id='upload-nav')
            ])
        ]),

        # Store for uploaded data info
        dcc.Store(id='file-info-store', data={}),
        dcc.Store(id='current-file-info-store'),


    ], fluid=True)


@callback(
    [
        Output('upload-results', 'children', allow_duplicate=True),
        Output('file-preview', 'children'),
        Output('file-info-store', 'data'),
        Output('upload-nav', 'children'),
        # Modal container output removed
        Output('current-file-info-store', 'data', allow_duplicate=True)
    ],
    [
        Input('upload-data', 'contents')
    ],
    [
        State('upload-data', 'filename')
    ],
    prevent_initial_call=True
)
def upload_callback(contents_list, filenames_list):
    """Handle file upload and processing"""
    if not contents_list:
        return "", "", {}, "", "", {}

    # Ensure contents and filenames are lists
    if not isinstance(contents_list, list):
        contents_list = [contents_list]
    if not isinstance(filenames_list, list):
        filenames_list = [filenames_list]

    upload_results = []
    file_info = {}
    preview_components = []
    verification_modal = ""
    current_file_info = {}

    for content, filename in zip(contents_list, filenames_list):
        try:
            # Process uploaded file
            result = process_uploaded_file(content, filename)

            if result['success']:
                df = result['data']
                rows = result['rows']
                cols = result['columns']
                upload_results.append(
                    dbc.Alert([
                        html.H6([
                            f"Successfully uploaded {filename} ({rows:,} rows, {cols} columns)"
                        ], className="alert-heading mb-2"),
                        dbc.Button(
                            "Verify Column Mappings",
                            id="verify-columns-btn-simple",
                            color="info",
                            size="sm",
                            className="mt-2"
                        )
                    ], color="success")
                )

                sample_data = {}
                for col in df.columns[:10]:
                    sample_data[col] = df[col].dropna().head(5).tolist()

                try:
                    from components.column_verification import get_ai_column_suggestions
                    ai_suggestions = get_ai_column_suggestions(df, filename)
                except Exception as e:
                    logger.warning(f"Could not get AI suggestions: {e}")
                    ai_suggestions = {}

                current_file_info = {
                    'filename': filename,
                    'columns': df.columns.tolist(),
                    'sample_data': sample_data,
                    'ai_suggestions': ai_suggestions,
                    'dataframe_shape': df.shape
                }

                try:
                    from components.column_verification import create_column_verification_modal
                    verification_modal = create_column_verification_modal(current_file_info)
                    print(f"✅ Modal created successfully for {filename}")
                    print(f"   Modal type: {type(verification_modal)}")

                    # Ensure it's a proper component
                    if not hasattr(verification_modal, 'children'):
                        print("❌ Modal is not a proper component, creating empty div")
                        verification_modal = html.Div()

                except Exception as e:
                    logger.error(f"❌ Error creating verification modal: {e}")
                    verification_modal = html.Div()  # Return empty div instead of empty string

                preview_components.append(create_file_preview(df, filename))

                file_info[filename] = {
                    'rows': rows,
                    'columns': cols,
                    'column_names': df.columns.tolist(),
                    'upload_time': result['upload_time']
                }

            else:
                upload_results.append(
                    dbc.Alert([
                        html.H6("Upload Failed", className="alert-heading"),
                        html.P(result['error'])
                    ], color="danger")
                )

        except Exception as e:
            logger.error(f"Error processing upload {filename}: {e}")
            upload_results.append(
                dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"❌ Error processing {filename}: {str(e)}"
                ], color="danger", className="mb-2")
            )

    # Create analytics navigation if files were uploaded successfully
    analytics_nav = html.Div([
        html.Hr(),
        html.H5("Ready to analyze?"),
        dbc.Button("Go to Analytics", href="/analytics", color="primary", size="lg", className="me-2"),
        dbc.Button("Upload More Files", id="upload-more-btn", color="outline-secondary", size="lg")
    ], className="mt-4")

    return (
        upload_results,
        preview_components,
        file_info,
        analytics_nav,
        current_file_info,
    )


def process_uploaded_file(contents, filename):
    """Process uploaded file content"""
    try:
        # Decode the base64 encoded file content
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        # Determine file type and parse accordingly
        if filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(decoded))
        elif filename.endswith('.json'):
            df = pd.read_json(io.StringIO(decoded.decode('utf-8')))
        else:
            return {
                'success': False,
                'error': f'Unsupported file type. Supported: CSV, Excel, JSON'
            }

        # Basic validation
        if df.empty:
            return {
                'success': False,
                'error': 'File appears to be empty'
            }

        # Store in global store (in production, use proper session/database storage)
        _uploaded_data_store[filename] = df

        return {
            'success': True,
            'data': df,
            'filename': filename,
            'rows': len(df),
            'columns': len(df.columns),
            'upload_time': pd.Timestamp.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing file {filename}: {e}")
        return {
            'success': False,
            'error': str(e)
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

        return dbc.Card([
            dbc.CardHeader([
                html.H6(f"📄 {filename}", className="mb-0")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("File Statistics:", className="text-primary"),
                        html.Ul([
                            html.Li(f"Rows: {num_rows:,}"),
                            html.Li(f"Columns: {num_cols}"),
                            html.Li(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                        ])
                    ], width=6),
                    dbc.Col([
                        html.H6("Columns:", className="text-primary"),
                        html.Ul([
                            html.Li(info) for info in column_info
                        ])
                    ], width=6)
                ]),

                html.Hr(),

                html.H6("Sample Data:", className="text-primary mt-3"),
                dbc.Table.from_dataframe(
                    df.head(5),
                    striped=True,
                    bordered=True,
                    hover=True,
                    responsive=True,
                    size="sm"
                )
            ])
        ], className="mb-3")

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
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'size_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
    return info


@callback(
    Output('upload-data', 'style'),
    Input('upload-more-btn', 'n_clicks'),
    prevent_initial_call=True
)
def highlight_upload_area(n_clicks):
    """Highlight upload area when 'upload more' is clicked"""
    if n_clicks:
        return {
            'width': '100%',
            'border': '3px dashed #28a745',
            'borderRadius': '8px',
            'textAlign': 'center',
            'cursor': 'pointer',
            'backgroundColor': '#d4edda',
            'animation': 'pulse 1s infinite'
        }
    return {
        'width': '100%',
        'border': '2px dashed #007bff',
        'borderRadius': '8px',
        'textAlign': 'center',
        'cursor': 'pointer',
        'backgroundColor': '#f8f9fa'
    }





@callback(
    Output('upload-results', 'children', allow_duplicate=True),
    Input('column-verify-confirm', 'n_clicks'),
    [State({"type": "field-mapping", "field": ALL}, "value"),
     State({"type": "field-mapping", "field": ALL}, "id"),
     State('current-file-info-store', 'data')],
    prevent_initial_call=True
)
def confirm_column_mappings(n_clicks, values, ids, file_info):
    """Fixed callback with correct component IDs"""
    if not n_clicks:
        return dash.no_update

    filename = file_info.get('filename', 'Unknown') if file_info else 'Unknown'

    # Build mappings
    mappings = {}
    for value, id_dict in zip(values or [], ids or []):
        if value and value != "skip":
            field = id_dict["field"]
            mappings[field] = value

    return dbc.Alert([
        html.H6("Mappings Confirmed!", className="alert-heading"),
        html.P(f"Mapped {len(mappings)} fields for {filename}")
    ], color="success", dismissable=True)


@callback(
    [Output({"type": "column-mapping", "index": ALL}, "value")],
    [Input("column-verify-ai-auto", "n_clicks")],
    [State("current-file-info-store", "data")],
    prevent_initial_call=True
)
def apply_ai_suggestions(n_clicks, file_info):
    """Apply AI suggestions automatically - RESTORED"""
    if not n_clicks or not file_info:
        return [dash.no_update]

    ai_suggestions = file_info.get('ai_suggestions', {})
    columns = file_info.get('columns', [])

    print(f"🤖 Applying AI suggestions for {len(columns)} columns")

    # Apply AI suggestions with confidence > 0.3
    suggested_values = []
    for column in columns:
        suggestion = ai_suggestions.get(column, {})
        confidence = suggestion.get('confidence', 0.0)
        field = suggestion.get('field', '')

        if confidence > 0.3 and field:
            suggested_values.append(field)
            print(f"   ✅ {column} -> {field} ({confidence:.0%})")
        else:
            suggested_values.append(None)
            print(f"   ❓ {column} -> No confident suggestion ({confidence:.0%})")

    return [suggested_values]


@callback(
    Output("column-verification-modal", "is_open"),
    [
        Input("verify-columns-btn-simple", "n_clicks"),
        Input("column-verify-cancel", "n_clicks"),
        Input("column-verify-confirm", "n_clicks"),
    ],
    [State("column-verification-modal", "is_open")],
    prevent_initial_call=True,
)
def toggle_verification_modal(verify_clicks, cancel_clicks, confirm_clicks, is_open):
    """Toggle the column verification modal with debugging"""
    import dash

    print(f"\U0001F527 Modal callback triggered!")
    print(f"   verify_clicks: {verify_clicks}")
    print(f"   cancel_clicks: {cancel_clicks}")
    print(f"   confirm_clicks: {confirm_clicks}")
    print(f"   current is_open: {is_open}")

    ctx = dash.callback_context
    if not ctx.triggered:
        print("   \u274C No trigger context")
        return False

    trigger_id = ctx.triggered[0]['prop_id']
    trigger_value = ctx.triggered[0]['value']

    print(f"   \U0001F3AF Triggered by: {trigger_id}")
    print(f"   \U0001F4CA Trigger value: {trigger_value}")

    if "verify-columns-btn" in trigger_id and trigger_value:
        print("   \u2705 Opening modal!")
        return True
    elif cancel_clicks or confirm_clicks:
        print("   \u274C Closing modal!")
        return False

    print("   \U0001F504 No change to modal state")
    return is_open


@callback(
    Output("column-verification-modal", "is_open", allow_duplicate=True),
    Input("verify-columns-btn-simple", "n_clicks"),
    prevent_initial_call=True,
)
def test_modal_open(n_clicks):
    """Simple test to open modal"""
    print(f"\U0001F9EA Simple button clicked! n_clicks: {n_clicks}")
    if n_clicks:
        return True
    return False


# Export functions for integration with other modules
__all__ = [
    'layout',
    'get_uploaded_data',
    'get_uploaded_filenames',
    'clear_uploaded_data',
    'get_file_info',
    'process_uploaded_file'
]
