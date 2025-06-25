#!/usr/bin/env python3
"""
Complete File Upload Page - Missing piece for consolidation
Integrates with analytics system
"""
import logging
import base64
import io
import pandas as pd
from typing import Optional, Dict, Any, List
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc

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
                html.Div(id='upload-status')
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

    ], fluid=True)


@callback(
    [
        Output('upload-status', 'children'),
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
                upload_results.append(
                    dbc.Alert([
                        html.I(className="fas fa-check-circle me-2"),
                        f"✅ Successfully uploaded {filename} ({result['rows']} rows, {result['columns']} columns)"
                    ], color="success", className="mb-2")
                )

                # Store file info
                file_info.append({
                    'filename': filename,
                    'rows': result['rows'],
                    'columns': result['columns'],
                    'upload_time': result['upload_time']
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


# Export functions for integration with other modules
__all__ = [
    'layout',
    'get_uploaded_data',
    'get_uploaded_filenames', 
    'clear_uploaded_data',
    'process_uploaded_file'
]
