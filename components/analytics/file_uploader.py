# components/analytics/file_uploader.py - Focused file uploader component
import dash_bootstrap_components as dbc
from dash import html, dcc
from typing import Optional

def create_file_uploader(upload_id: str = 'analytics-file-upload') -> html.Div:
    """Create file upload component for analytics page"""
    
    return html.Div([dbc.Card([
        dbc.CardHeader([
            html.H4("Data Upload & Analysis", className="mb-0"),
            html.Small("Upload CSV, JSON, or Excel files for analysis", className="text-muted")
        ]),
        dbc.CardBody([
            dcc.Upload(
                id=upload_id,
                children=html.Div([
                    html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                    html.H5("Drag and Drop or Click to Select Files"),
                    html.P("Supports: CSV, JSON, Excel (.xlsx, .xls)", className="text-muted"),
                    html.P("Maximum file size: 100MB", className="text-muted small")
                ]),
                style={
                    'width': '100%',
                    'height': '200px',
                    'lineHeight': '200px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'backgroundColor': '#fafafa',
                    'cursor': 'pointer'
                },
                multiple=True,
                accept='.csv,.json,.xlsx,.xls'
            ),
            html.Div(id='upload-status', className="mt-3"),
            html.Div(id='file-info', className="mt-3")
        ])
    ], className="mb-4")])
