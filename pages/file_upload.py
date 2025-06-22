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
        
        # Column mapping modal (initially hidden but all elements present)
        html.Div([
            # Modal overlay
            html.Div([
                html.Div([
                    # Modal header
                    html.Div([
                        html.H2("Verify AI Column Mapping", className="modal__title"),
                        html.P("", id="modal-subtitle", className="modal__subtitle"),
                        html.Button("×", id="close-mapping-modal", className="modal__close")
                    ], className="modal__header"),
                    
                    # Modal body
                    html.Div([
                        # Instructions
                        html.Div([
                            html.P("🤖 AI has analyzed your file and suggested column mappings below. Please verify and adjust as needed.",
                                   className="form-instructions-text"),
                            html.P("📊 Column mapping required",
                                   id="column-count-text", className="form-instructions-subtext")
                        ], className="form-instructions"),
                        
                        html.Hr(className="form-separator"),
                        
                        # Column mapping dropdowns (always present)
                        html.Div([
                            html.Div([
                                html.Label("Timestamp Column *", className="form-label form-label--required"),
                                html.Small("AI Suggestion: ", id="timestamp-suggestion", className="form-help-text"),
                                dcc.Dropdown(
                                    id="timestamp-dropdown",
                                    options=[],
                                    placeholder="Select a column...",
                                    className="form-select"
                                )
                            ], className="form-field"),
                            
                            html.Div([
                                html.Label("Device/Door Column", className="form-label"),
                                html.Small("AI Suggestion: ", id="device-suggestion", className="form-help-text"),
                                dcc.Dropdown(
                                    id="device-column-dropdown",
                                    options=[],
                                    placeholder="Select a column...",
                                    className="form-select"
                                )
                            ], className="form-field"),
                            
                            html.Div([
                                html.Label("User ID Column", className="form-label"),
                                html.Small("AI Suggestion: ", id="user-suggestion", className="form-help-text"),
                                dcc.Dropdown(
                                    id="user-id-dropdown",
                                    options=[],
                                    placeholder="Select a column...",
                                    className="form-select"
                                )
                            ], className="form-field"),
                            
                            html.Div([
                                html.Label("Event Type Column", className="form-label"),
                                html.Small("AI Suggestion: ", id="event-suggestion", className="form-help-text"),
                                dcc.Dropdown(
                                    id="event-type-dropdown",
                                    options=[],
                                    placeholder="Select a column...",
                                    className="form-select"
                                )
                            ], className="form-field")
                        ], className="form-grid"),
                        
                        html.Hr(className="form-separator"),
                        
                        # Floor estimate
                        html.Div([
                            html.Label("Number of Floors", className="form-label"),
                            dcc.Input(
                                id="floor-estimate-input",
                                type="number",
                                value=1,
                                min=1,
                                max=100,
                                className="form-input"
                            ),
                            html.Small("AI Confidence: 85%", id="floor-confidence", className="form-help-text")
                        ], className="form-field"),
                        
                        # Hidden storage
                        html.Div(id="user-id-storage", children="default", style={"display": "none"})
                        
                    ], className="modal__body"),
                    
                    # Modal footer
                    html.Div([
                        html.Button("Cancel", id="cancel-mapping", className="btn btn-secondary"),
                        html.Button("✅ Verify & Learn", id="verify-mapping", className="btn btn-primary")
                    ], className="modal__footer")
                    
                ], className="modal modal--xl")
            ], className="modal-overlay", style={"display": "none"})
        ], id='column-mapping-modal'),
        
        # Mapping verification status
        html.Div(id='mapping-verified-status', className="mt-4"),
        
        # Door mapping modal (initially hidden) 
        html.Div(id='door-mapping-modal', style={'display': 'none'}),
        
        # Data stores for the workflow
        dcc.Store(id='uploaded-file-store'),
        dcc.Store(id='processed-data-store'),
        dcc.Store(id='column-mapping-store')
    ])


def register_file_upload_callbacks(app, container=None):
    """Register file upload page callbacks - legacy support"""
    logger.info("File upload callbacks handled by @callback decorators in file_uploader.py")
    return True
