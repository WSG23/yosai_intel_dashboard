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
        ]
    )
