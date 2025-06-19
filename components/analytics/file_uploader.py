
from dash import html, dcc
import dash_bootstrap_components as dbc

def create_file_uploader(upload_id: str = 'analytics-file-upload') -> html.Div:
    """Create enhanced file uploader supporting CSV, JSON, and Excel"""
    
    return html.Div([dbc.Card([
        dbc.CardHeader([
            html.H4("📁 Data Upload & Analysis", className="mb-0"),
            html.Small("Upload CSV, JSON, or Excel files for analysis", className="text-muted")
        ]),
        dbc.CardBody([
            dcc.Upload(
                id=upload_id,
                children=html.Div([
                    html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                    html.H5("Drag and Drop or Click to Select Files"),
                    html.Div([
                        html.P("✅ CSV files (.csv)", className="text-success mb-1"),
                        html.P("✅ JSON files (.json)", className="text-success mb-1"),
                        html.P("✅ Excel files (.xlsx, .xls)", className="text-success mb-1"),
                    ], className="mt-3"),
                    html.P("Maximum file size: 100MB", className="text-muted small")
                ]),
                style={
                    'width': '100%',
                    'height': '250px',
                    'lineHeight': '60px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'backgroundColor': '#fafafa',
                    'cursor': 'pointer'
                },
                multiple=True,
                accept='.csv,.json,.xlsx,.xls,application/json,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,text/csv'
            ),
            html.Div(id='upload-status', className="mt-3"),
            html.Div(id='file-info', className="mt-3")
        ])
    ], className="mb-4")])
