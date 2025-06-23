"""
Enhanced File Upload Page with AI Integration and Dual Loading
"""
from dash import html, dcc
import logging
from components.analytics.file_uploader import create_dual_file_uploader

logger = logging.getLogger(__name__)


def layout():
    """Simplified file upload page that definitely works"""
    return html.Div([
        # Page header
        html.Div([
            html.H1("🏯 File Upload & Processing", className="text-3xl font-bold mb-4"),
            html.P("Upload CSV, JSON, and Excel files for security analytics processing",
                   className="text-lg text-gray-600 mb-8")
        ], className="text-center mb-8"),

        # File uploader (this should work)
        create_dual_file_uploader('upload-data'),

        # Status messages (initially empty)
        html.Div(id='upload-status', className="mt-6"),
        html.Button(
            "Continue to Column Mapping",
            id="open-column-mapping",
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded",
            style={"display": "none"},
        ),
        html.Div(id='upload-info', className="mt-4"),

        # Column mapping modal (hidden initially)
        html.Div([
            html.Div([
                html.Div([
                    # Modal header
                    html.Div([
                        html.H2("🤖 Verify AI Column Mapping", className="text-xl font-bold"),
                        html.P("", id="modal-subtitle", className="text-gray-600"),
                        html.Button("✕", id="close-mapping-modal",
                                   className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl")
                    ], className="relative mb-6"),

                    # Modal body
                    html.Div([
                        html.P("🤖 AI has analyzed your file and suggested column mappings below. Please verify and adjust as needed.",
                               className="mb-4 text-blue-600"),
                        html.P("📊 Column mapping required", id="column-count-text", className="mb-6 text-gray-600"),

                        # Column dropdowns
                        html.Div([
                            # Timestamp column
                            html.Div([
                                html.Label("Timestamp Column *", className="block font-medium mb-2"),
                                html.Small("AI Suggestion: ", id="timestamp-suggestion", className="text-green-600 text-sm"),
                                dcc.Dropdown(
                                    id="timestamp-dropdown",
                                    options=[],
                                    placeholder="Select timestamp column...",
                                    className="mb-4"
                                )
                            ], className="mb-4"),

                            # Device column
                            html.Div([
                                html.Label("Device/Door Column", className="block font-medium mb-2"),
                                html.Small("AI Suggestion: ", id="device-suggestion", className="text-green-600 text-sm"),
                                dcc.Dropdown(
                                    id="device-column-dropdown",
                                    options=[],
                                    placeholder="Select device column...",
                                    className="mb-4"
                                )
                            ], className="mb-4"),

                            # User ID column
                            html.Div([
                                html.Label("User ID Column", className="block font-medium mb-2"),
                                html.Small("AI Suggestion: ", id="user-suggestion", className="text-green-600 text-sm"),
                                dcc.Dropdown(
                                    id="user-id-dropdown",
                                    options=[],
                                    placeholder="Select user ID column...",
                                    className="mb-4"
                                )
                            ], className="mb-4"),

                            # Event type column
                            html.Div([
                                html.Label("Event Type Column", className="block font-medium mb-2"),
                                html.Small("AI Suggestion: ", id="event-suggestion", className="text-green-600 text-sm"),
                                dcc.Dropdown(
                                    id="event-type-dropdown",
                                    options=[],
                                    placeholder="Select event type column...",
                                    className="mb-4"
                                )
                            ], className="mb-4"),

                            # Floor estimate
                            html.Div([
                                html.Label("Floor Estimate", className="block font-medium mb-2"),
                                dcc.Input(
                                    id="floor-estimate-input",
                                    type="number",
                                    value=1,
                                    min=1,
                                    max=100,
                                    className="w-full p-2 border rounded"
                                ),
                                html.Small("AI Confidence: ", id="floor-confidence", className="text-green-600 text-sm")
                            ], className="mb-6"),

                        ], className="space-y-4"),

                    ], className="mb-6"),

                    # Modal footer
                    html.Div([
                        html.Button("Cancel", id="cancel-mapping",
                                   className="px-4 py-2 mr-2 bg-gray-500 text-white rounded hover:bg-gray-600"),
                        html.Button("✅ Verify & Learn", id="verify-mapping",
                                   className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600")
                    ], className="flex justify-end")

                ], className="bg-white p-6 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto")
            ], className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50",
               style={"display": "none"}, id="column-mapping-modal-overlay")
        ]),

        # Results area
        html.Div(id='mapping-verified-status', className="mt-6"),

        # Next step buttons (hidden initially)
        html.Div([
            html.Button("Proceed to Door Mapping", id="door-mapping-modal-trigger",
                       className="px-6 py-2 mr-2 bg-green-500 text-white rounded hover:bg-green-600",
                       style={"display": "none"}),
            html.Button("Skip Door Mapping", id="skip-door-mapping",
                       className="px-6 py-2 bg-gray-500 text-white rounded hover:bg-gray-600",
                       style={"display": "none"})
        ], className="mt-4"),

        # Door mapping modal placeholder
        html.Div(id='door-mapping-modal', style={'display': 'none'}),

        # Data stores
        dcc.Store(id='uploaded-file-store', data={}),
        dcc.Store(id='processed-data-store', data={}),
        dcc.Store(id='column-mapping-store', data={}),
        dcc.Store(id='door-mapping-store', data={}),
        dcc.Store(id='floor-estimate-store', data={}),
        dcc.Store(id='door-mapping-modal-data-trigger', data={}),

        # Hidden user ID storage
        html.Div(id="user-id-storage", children="default", style={"display": "none"})

    ], className="container mx-auto px-4 py-8")


def register_file_upload_callbacks(app, container=None):
    """Register file upload page callbacks - legacy support"""
    logger.info("File upload callbacks handled by @callback decorators in file_uploader.py")
    return True
