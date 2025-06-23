"""
Enhanced File Upload Page with AI Integration and Dual Loading
"""
from dash import html, dcc
import logging
from components.analytics.file_uploader import create_dual_file_uploader

logger = logging.getLogger(__name__)


def layout():
    """File upload page layout with proper accessibility"""
    from components.analytics.session_loader import create_session_loader

    return html.Div([
        # Page header
        html.Div([
            html.H1("🏢 File Upload & Processing", className="page-title"),
            html.P("Upload CSV, JSON, and Excel files for security analytics processing",
                   className="page-subtitle")
        ], className="page-header"),

        # Two-column layout
        html.Div([
            # Left column - New upload
            html.Div([
                html.H2("📤 New Upload", className="text-xl font-semibold mb-4"),
                create_dual_file_uploader('upload-data'),
            ], className="w-1/2 pr-4"),

            # Right column - Previous uploads  
            html.Div([
                create_session_loader()
            ], className="w-1/2 pl-4")

        ], className="flex gap-8 mb-8"),

        # Status displays
        html.Div(id='upload-status', className="mt-4"),
        html.Div(id='upload-info', className="mt-3"),

        # Column mapping modal (with proper accessibility)
        html.Div([
            html.Div([
                html.Div([
                    # Modal header
                    html.Div([
                        html.H2("Verify AI Column Mapping",
                               className="modal__title",
                               id="modal-title"),
                        html.P("",
                               id="modal-subtitle",
                               className="modal__subtitle"),
                        html.Button("×",
                                   id="close-mapping-modal",
                                   className="modal__close",
                                   **{"aria-label": "Close modal"})
                    ], className="modal__header"),

                    # Modal body
                    html.Div([
                        # Instructions
                        html.Div([
                            html.P("🤖 AI has analyzed your file and suggested column mappings below. Please verify and adjust as needed.",
                                   className="form-instructions-text"),
                            html.P("📊 Column mapping required",
                                   id="column-count-text",
                                   className="form-instructions-subtext")
                        ], className="form-instructions"),

                        html.Hr(className="form-separator"),

                        # Form with proper labels and IDs
                        html.Form([
                            html.Div([
                                html.Label("Timestamp Column *",
                                          htmlFor="timestamp-dropdown",
                                          className="form-label form-label--required"),
                                html.Small("AI Suggestion: ",
                                          id="timestamp-suggestion",
                                          className="form-help-text"),
                                dcc.Dropdown(
                                    id="timestamp-dropdown",
                                    options=[],
                                    placeholder="Select a column...",
                                    className="form-select"
                                )
                            ], className="form-field"),

                            html.Div([
                                html.Label("Device/Door Column",
                                          htmlFor="device-column-dropdown",
                                          className="form-label"),
                                html.Small("AI Suggestion: ",
                                          id="device-suggestion",
                                          className="form-help-text"),
                                dcc.Dropdown(
                                    id="device-column-dropdown",
                                    options=[],
                                    placeholder="Select a column...",
                                    className="form-select"
                                )
                            ], className="form-field"),

                            html.Div([
                                html.Label("User ID Column",
                                          htmlFor="user-id-dropdown",
                                          className="form-label"),
                                html.Small("AI Suggestion: ",
                                          id="user-suggestion",
                                          className="form-help-text"),
                                dcc.Dropdown(
                                    id="user-id-dropdown",
                                    options=[],
                                    placeholder="Select a column...",
                                    className="form-select"
                                )
                            ], className="form-field"),

                            html.Div([
                                html.Label("Event Type Column",
                                          htmlFor="event-type-dropdown",
                                          className="form-label"),
                                html.Small("AI Suggestion: ",
                                          id="event-suggestion",
                                          className="form-help-text"),
                                dcc.Dropdown(
                                    id="event-type-dropdown",
                                    options=[],
                                    placeholder="Select a column...",
                                    className="form-select"
                                )
                            ], className="form-field"),

                            html.Div([
                                html.Label("Floor Estimate",
                                          htmlFor="floor-estimate-input",
                                          className="form-label"),
                                html.Small("AI Confidence: 85%",
                                          id="floor-confidence",
                                          className="form-help-text"),
                                dcc.Input(
                                    id="floor-estimate-input",
                                    name="floor-estimate",
                                    type="number",
                                    value=1,
                                    min=1,
                                    max=100,
                                    className="form-input"
                                )
                            ], className="form-field"),

                            # Hidden storage
                            html.Div(id="user-id-storage",
                                     children="default",
                                     style={"display": "none"})

                        ], className="modal__body-content"),

                    ], className="modal__body"),

                    # Modal footer
                    html.Div([
                        html.Button("Cancel",
                                   id="cancel-mapping",
                                   className="btn btn-secondary"),
                        html.Button("✅ Verify & Learn",
                                   id="verify-mapping",
                                   className="btn btn-primary")
                    ], className="modal__footer")

                ], className="modal modal--xl")
            ], className="modal-overlay",
               style={"display": "none"},
               id="column-mapping-modal-overlay",
               role="dialog",
               **{"aria-labelledby": "modal-title"})
        ], id='column-mapping-modal'),

        # Mapping verification status
        html.Div(id='mapping-verified-status', className="mt-4"),

        # Door mapping modal
        html.Div(id='door-mapping-modal', style={'display': 'none'}),

        # Action buttons
        html.Button("Proceed to Door Mapping",
                   id="open-door-mapping",
                   className="btn btn-primary mt-3 mr-2",
                   style={"display": "none"}),
        html.Button("Skip Door Mapping",
                   id="skip-door-mapping",
                   className="btn btn-secondary mt-3",
                   style={"display": "none"}),

        # Data stores
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
