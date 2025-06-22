"""
Enhanced File Upload Page with AI Integration and Dual Loading
"""
from dash import html, dcc
import logging
from components.analytics.file_uploader import create_dual_file_uploader

logger = logging.getLogger(__name__)


def layout():
    """File upload page layout with dual upload functionality and all modal elements"""
    return html.Div([
        # Page header
        html.Div([
            html.H1("\U0001F3EF File Upload & Processing", className="page-title"),
            html.P("Upload CSV, JSON, and Excel files for security analytics processing",
                   className="page-subtitle")
        ], className="page-header"),
        
        # Main upload interface
        create_dual_file_uploader('upload-data'),
        
        # Status displays
        html.Div(id='upload-status', className="mt-4"),
        html.Div(id='upload-info', className="mt-3"),
        
        # Column mapping modal (dynamically generated)
        html.Div(id='column-mapping-modal'),
        
        # Mapping verification status
        html.Div(id='mapping-verified-status', className="mt-4"),
        
        # Door mapping modal (initially hidden) 
        html.Div(id='door-mapping-modal', style={'display': 'none'}),
        
        # Data stores for the workflow - THESE WERE MISSING
        dcc.Store(id='uploaded-file-store'),
        dcc.Store(id='processed-data-store'),
        dcc.Store(id='column-mapping-store'),
        dcc.Store(id='door-mapping-store'),
        dcc.Store(id='floor-estimate-store'),
        dcc.Store(id='door-mapping-modal-data-trigger'),
    ])


def register_file_upload_callbacks(app, container=None):
    """Register file upload page callbacks - legacy support"""
    logger.info("File upload callbacks handled by @callback decorators in file_uploader.py")
    return True
