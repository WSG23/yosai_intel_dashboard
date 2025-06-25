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
from dash import html, dcc, callback, Input, Output, State, ALL
import dash
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
                html.Div(id='file-preview-area')
            ])
        ]),

        # Navigation to analytics
        dbc.Row([
            dbc.Col([
                html.Div(id='analytics-navigation')
            ])
        ]),

        # Store for uploaded data info
        dcc.Store(id='uploaded-files-store', data=[]),
        dcc.Store(id='current-file-info-store'),

        # Container for column verification modal
        html.Div(id='column-verification-modal-container'),

    ], fluid=True)


@callback(
    [
        Output('upload-results', 'children'),
        Output('file-preview-area', 'children'),
        Output('uploaded-files-store', 'data'),
        Output('analytics-navigation', 'children')
    ],
    [
        Input('upload-data', 'contents')
    ],
    [
        State('upload-data', 'filename'),
        State('uploaded-files-store', 'data')
    ],
    prevent_initial_call=True
)
def handle_file_upload(contents, filenames, existing_files):
    """Handle file upload and processing"""
    if not contents:
        return "", "", existing_files, ""

    # Ensure contents and filenames are lists
    if not isinstance(contents, list):
        contents = [contents]
    if not isinstance(filenames, list):
        filenames = [filenames]

    upload_results = []
    file_info = existing_files.copy() if existing_files else []
    preview_components = []

    for content, filename in zip(contents, filenames):
        try:
            # Process uploaded file
            result = process_uploaded_file(content, filename)

            if result['success']:
                rows = result['rows']
                cols = result['columns']
                upload_results.append(
                    dbc.Alert([
                        html.H6([
                            f"Successfully uploaded {filename} ({rows:,} rows, {cols} columns)"
                        ], className="alert-heading mb-2"),
                        dbc.Button(
                            "Verify Column Mappings",
                            id={"type": "verify-columns-btn", "filename": filename},
                            color="info",
                            size="sm",
                            className="mt-2"
                        )
                    ], color="success")
                )

                # Store file info
                file_info.append({
                    'filename': filename,
                    'rows': result['rows'],
                    'columns': result['columns'],
                    'upload_time': result['upload_time'],
                    'column_names': list(result['data'].columns)
                })

                # Create preview
                preview_components.append(create_file_preview(result['data'], filename))

            else:
                upload_results.append(
                    dbc.Alert([
                        html.I(className="fas fa-exclamation-triangle me-2"),
                        f"❌ Failed to upload {filename}: {result['error']}"
                    ], color="danger", className="mb-2")
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
    analytics_nav = ""
    if any('success' in str(result) for result in upload_results):
        analytics_nav = dbc.Card([
            dbc.CardBody([
                html.H5("🚀 Ready for Analytics", className="text-success mb-3"),
                html.P("Your files have been uploaded successfully. Ready to analyze?"),
                dbc.Button(
                    "📊 Go to Analytics",
                    href="/analytics", 
                    color="primary",
                    size="lg",
                    className="me-2"
                ),
                dbc.Button(
                    "📁 Upload More Files",
                    id="upload-more-btn",
                    color="outline-secondary",
                    size="lg"
                )
            ])
        ], className="mt-4")

    return upload_results, preview_components, file_info, analytics_nav


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
    Output('column-verification-modal-container', 'children'),
    Output('current-file-info-store', 'data'),
    Input({'type': 'verify-columns-btn', 'filename': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def show_column_verification(n_clicks_list):
    """Display column verification modal when user opts to verify"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    triggered = ctx.triggered[0]['prop_id'].split('.')[0]
    try:
        btn_id = json.loads(triggered)
        filename = btn_id.get('filename')
    except Exception:
        return dash.no_update, dash.no_update

    df = _uploaded_data_store.get(filename)
    if df is None:
        return dash.no_update, dash.no_update

    sample_data = {col: df[col].dropna().astype(str).head(5).tolist() for col in df.columns}
    file_info = {
        'filename': filename,
        'columns': list(df.columns),
        'sample_data': sample_data,
        'ai_suggestions': get_ai_column_suggestions(df, filename)
    }
    modal = create_column_verification_modal(file_info)
    modal.is_open = True
    return modal, file_info


@callback(
    Output('column-verification-modal-container', 'children'),
    [Input('column-verify-cancel', 'n_clicks'), Input('column-verify-confirm', 'n_clicks')],
    prevent_initial_call=True
)
def close_column_verification(cancel_clicks, confirm_clicks):
    """Close verification modal on cancel or confirm"""
    if cancel_clicks or confirm_clicks:
        return ''
    return dash.no_update


@callback(
    Output('upload-results', 'children', allow_duplicate=True),
    [Input('column-verify-confirm', 'n_clicks')],
    [State({'type': 'column-mapping', 'index': ALL}, 'value'),
     State({'type': 'custom-field', 'index': ALL}, 'value'),
     State('training-data-source-type', 'value'),
     State('training-data-quality', 'value'),
     State('current-file-info-store', 'data')],
    prevent_initial_call=True
)
def confirm_column_mappings(n_clicks, mapping_values, custom_values, data_source_type, data_quality, file_info):
    """Handle confirmed column mappings"""
    if not n_clicks or not file_info:
        return dash.no_update

    try:
        filename = file_info.get('filename', 'unknown')
        columns = file_info.get('columns', [])

        column_mappings = {}
        for column, mapping_value, custom_value in zip(columns, mapping_values, custom_values):
            if mapping_value == 'other' and custom_value:
                column_mappings[column] = custom_value.strip()
            elif mapping_value and mapping_value != 'ignore':
                column_mappings[column] = mapping_value

        metadata = {
            'data_source_type': data_source_type,
            'data_quality': data_quality,
            'num_columns': len(columns),
            'num_mapped': len(column_mappings),
            'verification_timestamp': datetime.now().isoformat()
        }

        success = save_verified_mappings(filename, column_mappings, metadata)

        if success:
            return dbc.Alert([
                html.H6('Column Mappings Verified Successfully!', className='alert-heading mb-2'),
                html.P([
                    f'Saved {len(column_mappings)} column mappings for ',
                    html.Strong(filename),
                    '. This data will help improve AI suggestions for future uploads.'
                ]),
                html.Small('AI training data updated', className='text-muted')
            ], color='success', dismissable=True)
        else:
            return dbc.Alert([
                html.H6('Verification Saved Locally', className='alert-heading'),
                html.P("Column mappings confirmed but couldn't save to AI training system.")
            ], color='warning', dismissable=True)

    except Exception as e:
        logger.error(f'Error confirming column mappings: {e}')
        return dbc.Alert([
            html.H6('Verification Error', className='alert-heading'),
            html.P(f'Error saving column mappings: {str(e)}')
        ], color='danger', dismissable=True)


# Export functions for integration with other modules
__all__ = [
    'layout',
    'get_uploaded_data',
    'get_uploaded_filenames',
    'clear_uploaded_data',
    'get_file_info',
    'process_uploaded_file'
]
