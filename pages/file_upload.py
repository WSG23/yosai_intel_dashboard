"""
Enhanced File Upload Page with AI Integration and Dual Loading
"""

from dash import html, dcc
import logging
from components.analytics.file_uploader import create_dual_file_uploader

logger = logging.getLogger(__name__)


def layout():
    """Enhanced file upload page with AI column mapping"""
    return html.Div(
        [
            html.Div(
                [
                    html.H1(
                        "🏯 File Upload & Processing",
                        className="text-3xl font-bold mb-4",
                    ),
                    html.P(
                        "Upload CSV, JSON, and Excel files for security analytics processing",
                        className="text-lg text-gray-600 mb-8",
                    ),
                ],
                className="text-center mb-8",
            ),
            create_dual_file_uploader("upload-data"),
            html.Div(id="upload-status-message", className="mt-6"),
            # Enhanced modal for AI column mapping verification
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    # Modal header
                                    html.Div(
                                        [
                                            html.H2("🤖 Verify AI Column Mapping", className="text-xl font-bold"),
                                            html.P("", id="modal-file-info", className="text-gray-600"),
                                            html.Button(
                                                "✕",
                                                id="close-mapping-modal",
                                                className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl",
                                            ),
                                        ],
                                        className="relative mb-6",
                                    ),

                                    # ENHANCED COLUMN MAPPING SECTION
                                    html.Div(
                                        [
                                            html.P(
                                                "🤖 AI has analyzed your file and suggested column mappings below. Green checkmarks indicate high confidence matches.",
                                                className="text-sm text-gray-600 mb-4",
                                            ),

                                            # Column mapping grid
                                            html.Div(
                                                [
                                                    # Timestamp mapping
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "⏰ Timestamp Column *",
                                                                className="block text-sm font-medium text-gray-700 mb-2",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    dcc.Dropdown(
                                                                        id="timestamp-dropdown",
                                                                        placeholder="Select timestamp column...",
                                                                        className="flex-1",
                                                                    ),
                                                                    html.Div(id="timestamp-confidence", className="ml-2 flex items-center"),
                                                                ],
                                                                className="flex items-center",
                                                            ),
                                                        ],
                                                        className="mb-4",
                                                    ),

                                                    # Device mapping
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "🚪 Device/Door Column",
                                                                className="block text-sm font-medium text-gray-700 mb-2",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    dcc.Dropdown(
                                                                        id="device-dropdown",
                                                                        placeholder="Select device column...",
                                                                        className="flex-1",
                                                                    ),
                                                                    html.Div(id="device-confidence", className="ml-2 flex items-center"),
                                                                ],
                                                                className="flex items-center",
                                                            ),
                                                        ],
                                                        className="mb-4",
                                                    ),

                                                    # User mapping
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "👤 User ID Column",
                                                                className="block text-sm font-medium text-gray-700 mb-2",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    dcc.Dropdown(
                                                                        id="user-dropdown",
                                                                        placeholder="Select user column...",
                                                                        className="flex-1",
                                                                    ),
                                                                    html.Div(id="user-confidence", className="ml-2 flex items-center"),
                                                                ],
                                                                className="flex items-center",
                                                            ),
                                                        ],
                                                        className="mb-4",
                                                    ),

                                                    # Event mapping
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "📝 Event Type Column",
                                                                className="block text-sm font-medium text-gray-700 mb-2",
                                                            ),
                                                            html.Div(
                                                                [
                                                                    dcc.Dropdown(
                                                                        id="event-dropdown",
                                                                        placeholder="Select event column...",
                                                                        className="flex-1",
                                                                    ),
                                                                    html.Div(id="event-confidence", className="ml-2 flex items-center"),
                                                                ],
                                                                className="flex items-center",
                                                            ),
                                                        ],
                                                        className="mb-6",
                                                    ),
                                                ],
                                                className="space-y-4",
                                            ),

                                            # COLUMN PREVIEW SECTION
                                            html.Div(
                                                [
                                                    html.H4(
                                                        "📋 Available Columns",
                                                        className="text-sm font-medium text-gray-700 mb-2",
                                                    ),
                                                    html.Div(
                                                        id="column-preview-list",
                                                        className="bg-gray-50 p-3 rounded max-h-32 overflow-y-auto",
                                                    ),
                                                ],
                                                className="mb-4",
                                            ),

                                            # Action buttons
                                            html.Div(
                                                [
                                                    dbc.Button(
                                                        "✅ Verify Mapping",
                                                        id="verify-mapping",
                                                        color="primary",
                                                        className="mr-2",
                                                    ),
                                                    dbc.Button(
                                                        "Cancel",
                                                        id="close-mapping-modal",
                                                        color="secondary",
                                                    ),
                                                ],
                                                className="flex justify-end space-x-2",
                                            ),
                                        ],
                                        className="p-4",
                                    ),
                                ],
                                className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto",
                            ),
                        ]
                    ),
                ],
                className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50",
                id="column-mapping-modal",
                style={"display": "none"},
            ),
            # Hidden stores for data persistence
            dcc.Store(id="uploaded-file-store"),
            dcc.Store(id="processed-data-store"),
            # Next step button (initially hidden)
            html.Div(
                [
                    html.Button(
                        "📍 Proceed to Device Mapping",
                        id="proceed-to-device-mapping-btn",
                        className="px-6 py-3 bg-green-600 text-white rounded-lg font-medium",
                    ),
                ],
                id="proceed-to-device-mapping",
                className="text-center mt-6",
                style={"display": "none"},  # Initially hidden
            ),
        ]
    )
