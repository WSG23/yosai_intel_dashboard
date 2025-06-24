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
            # FIXED: Add proper modal wrapper with correct id and initial hidden state
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    # Modal header
                                    html.Div(
                                        [
                                            html.H2(
                                                "🤖 Verify AI Column Mapping",
                                                className="text-xl font-bold",
                                            ),
                                            html.P(
                                                "",
                                                id="modal-file-info",
                                                className="text-gray-600",
                                            ),
                                            html.Button(
                                                "✕",
                                                id="close-mapping-modal",
                                                className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 text-2xl",
                                            ),
                                        ],
                                        className="relative mb-6",
                                    ),
                                    # Modal body
                                    html.Div(
                                        [
                                            html.P(
                                                "🤖 AI has analyzed your file and suggested column mappings below. Please verify and adjust as needed.",
                                                className="text-gray-700 mb-6",
                                            ),
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "🕐 Timestamp Column:",
                                                                className="block text-sm font-medium mb-1",
                                                            ),
                                                            dcc.Dropdown(
                                                                id="timestamp-dropdown",
                                                                placeholder="Select timestamp column...",
                                                                className="mb-3",
                                                            ),
                                                        ],
                                                        className="mb-4",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "🚪 Device/Door Column:",
                                                                className="block text-sm font-medium mb-1",
                                                            ),
                                                            dcc.Dropdown(
                                                                id="device-dropdown",
                                                                placeholder="Select device column...",
                                                                className="mb-3",
                                                            ),
                                                        ],
                                                        className="mb-4",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "👤 User/Person Column:",
                                                                className="block text-sm font-medium mb-1",
                                                            ),
                                                            dcc.Dropdown(
                                                                id="user-dropdown",
                                                                placeholder="Select user column...",
                                                                className="mb-3",
                                                            ),
                                                        ],
                                                        className="mb-4",
                                                    ),
                                                    html.Div(
                                                        [
                                                            html.Label(
                                                                "📋 Event Type Column:",
                                                                className="block text-sm font-medium mb-1",
                                                            ),
                                                            dcc.Dropdown(
                                                                id="event-dropdown",
                                                                placeholder="Select event column...",
                                                                className="mb-3",
                                                            ),
                                                        ],
                                                        className="mb-4",
                                                    ),
                                                ],
                                                className="grid grid-cols-1 gap-4",
                                            ),
                                        ]
                                    ),
                                    # Modal footer
                                    html.Div(
                                        [
                                            html.Button(
                                                "❌ Cancel",
                                                id="close-mapping-modal",
                                                className="px-4 py-2 bg-gray-500 text-white rounded mr-2",
                                            ),
                                            html.Button(
                                                "✅ Verify & Continue",
                                                id="verify-mapping",
                                                className="px-4 py-2 bg-blue-600 text-white rounded",
                                            ),
                                        ],
                                        className="flex justify-end mt-6",
                                    ),
                                ],
                                className="bg-white p-6 rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto",
                            ),
                        ],
                        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4",
                    ),
                ],
                id="column-mapping-modal",
                style={"display": "none"},  # FIXED: Initially hidden
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
