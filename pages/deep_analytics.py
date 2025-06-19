"""
Deep Analytics page with safe text handling
UPDATED: Removed babel dependency, uses safe text functions
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
from typing import List, Dict, Any, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)

# Safe text function that works without babel
def safe_text(text: str) -> str:
    """Return text safely, handling any babel objects"""
    return str(text)

# Import the modular analytics components with safe fallbacks
try:
    from components.analytics import (
        create_file_uploader,
        create_data_preview,
        create_analytics_charts,
        create_summary_cards,
        FileProcessor,
        AnalyticsGenerator,
    )

    ANALYTICS_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Analytics components not fully available: {e}")
    ANALYTICS_COMPONENTS_AVAILABLE = False

    # Create fallback functions
    def create_file_uploader(*args, **kwargs):
        return html.Div(safe_text("File uploader not available"))

    def create_data_preview(*args, **kwargs):
        return html.Div(safe_text("Data preview not available"))

    def create_analytics_charts(*args, **kwargs):
        return html.Div(safe_text("Charts not available"))

    def create_summary_cards(*args, **kwargs):
        return html.Div(safe_text("Summary cards not available"))

    class FallbackFileProcessor:
        @staticmethod
        def process_file_content(contents, filename):
            return None

        @staticmethod
        def validate_dataframe(df):
            return False, "FileProcessor not available", []

    class FallbackAnalyticsGenerator:
        @staticmethod
        def generate_analytics(df):
            return {}

# Assign fallback classes to main names if analytics components are unavailable
if not ANALYTICS_COMPONENTS_AVAILABLE:
    FileProcessor = FallbackFileProcessor
    AnalyticsGenerator = FallbackAnalyticsGenerator


def layout():
    """Deep Analytics page layout"""
    return dbc.Container(
        [
            # Page header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1(
                                safe_text("🔍 Deep Analytics"), className="text-primary mb-0"
                            ),
                            html.P(
                                safe_text(
                                    "Advanced data analysis and visualization for security intelligence"
                                ),
                                className="text-secondary mb-4",
                            ),
                        ]
                    )
                ]
            ),
            # File upload section
            dbc.Row([dbc.Col([create_file_uploader("analytics-file-upload")])]),
            # Data storage for uploaded files
            dcc.Store(id="uploaded-data-store", data={}),
            # Results section
            html.Div(id="analytics-results", children=[]),
        ],
        fluid=True,
        className="p-4",
    )


def register_analytics_callbacks(app, container=None):
    """Register analytics page callbacks with DI container"""

    if not ANALYTICS_COMPONENTS_AVAILABLE:
        print("Warning: Analytics callbacks not registered - components not available")
        return

    @app.callback(
        [
            Output("upload-status", "children"),
            Output("uploaded-data-store", "data"),
            Output("analytics-results", "children"),
        ],
        Input("analytics-file-upload", "contents"),
        State("analytics-file-upload", "filename"),
        prevent_initial_call=True,
    )
    def process_uploaded_files(
        contents_list: Optional[Union[str, List[str]]],
        filename_list: Optional[Union[str, List[str]]],
    ) -> Tuple[html.Div, Dict[str, Any], html.Div]:
        """Process uploaded files and generate analytics"""
        
        if not contents_list:
            return (
                html.Div(),
                {},
                html.Div(),
            )

        # Ensure inputs are lists
        if isinstance(contents_list, str):
            contents_list = [contents_list]
        if isinstance(filename_list, str):
            filename_list = [filename_list]

        upload_status = []
        all_data = []
        errors = []

        # Process each uploaded file
        for contents, filename in zip(contents_list, filename_list):
            try:
                # Process file content
                processed_data = FileProcessor.process_file_content(contents, filename)
                
                if processed_data is not None:
                    # Validate the dataframe
                    is_valid, message, suggestions = FileProcessor.validate_dataframe(
                        processed_data
                    )
                    
                    if is_valid:
                        upload_status.append(_create_success_alert(
                            safe_text(f"✅ {filename} uploaded successfully ({len(processed_data)} rows)")
                        ))
                        all_data.append({
                            "filename": filename,
                            "data": processed_data.to_dict("records"),
                            "shape": processed_data.shape,
                        })
                    else:
                        upload_status.append(_create_warning_alert(
                            safe_text(f"⚠️ {filename}: {message}")
                        ))
                        errors.append(f"{filename}: {message}")
                else:
                    upload_status.append(_create_error_alert(
                        safe_text(f"❌ Failed to process {filename}")
                    ))
                    errors.append(f"Failed to process {filename}")
                    
            except Exception as e:
                error_msg = safe_text(f"❌ Error processing {filename}: {str(e)}")
                upload_status.append(_create_error_alert(error_msg))
                errors.append(error_msg)

        # Generate analytics if we have valid data
        analytics_results = html.Div()
        if all_data:
            try:
                # Combine all uploaded data
                combined_df = _combine_uploaded_data(all_data)
                
                if not combined_df.empty:
                    # Generate analytics using the service if available
                    analytics_service = container.get('analytics_service') if container else None
                    analytics_data = _generate_analytics_with_service(
                        combined_df, analytics_service, len(all_data)
                    )
                    
                    # Create analytics display components
                    analytics_results = html.Div([
                        html.Hr(),
                        html.H3(safe_text("📊 Analytics Results"), className="text-primary"),
                        create_summary_cards(analytics_data, combined_df),
                        create_data_preview(combined_df),
                        create_analytics_charts(analytics_data, combined_df),
                    ])
                    
            except Exception as e:
                analytics_results = _create_error_alert(
                    safe_text(f"Error generating analytics: {str(e)}")
                )

        return (
            html.Div(upload_status),
            {"files": all_data, "errors": errors},
            analytics_results,
        )


def _generate_analytics_with_service(
    combined_df: pd.DataFrame, 
    analytics_service: Optional[Any], 
    num_files: int
) -> Dict[str, Any]:
    """Generate analytics using injected service or fallback"""
    
    if analytics_service is not None:
        try:
            analytics_data = analytics_service.process_uploaded_file(
                combined_df, f"Combined Data ({num_files} files)"
            )
            if analytics_data.get("success", False):
                return analytics_data["analytics"]
            return {}
        except Exception as e:
            print(f"Error using injected analytics service: {e}")
            return AnalyticsGenerator.generate_analytics(combined_df)

    return AnalyticsGenerator.generate_analytics(combined_df)


def _combine_uploaded_data(all_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Combine multiple uploaded files into a single DataFrame"""
    combined_df = pd.DataFrame()

    for file_data in all_data:
        try:
            file_df = pd.DataFrame(file_data["data"])
            combined_df = pd.concat(
                [combined_df, file_df], ignore_index=True, sort=False
            )
        except Exception as e:
            print(
                f"Error combining data from {file_data.get('filename', 'unknown')}: {e}"
            )
            continue

    return combined_df


def _create_success_alert(message: str) -> html.Div:
    """Create a success alert message"""
    alert = dbc.Alert(
        [html.I(className="fas fa-check-circle me-2"), message],
        color="success",
        className="mb-2",
    )
    return html.Div(alert)


def _create_warning_alert(message: str) -> html.Div:
    """Create a warning alert message"""
    alert = dbc.Alert(
        [html.I(className="fas fa-exclamation-triangle me-2"), message],
        color="warning",
        className="mb-2",
    )
    return html.Div(alert)


def _create_error_alert(message: str) -> html.Div:
    """Create an error alert message"""
    alert = dbc.Alert(
        [html.I(className="fas fa-times-circle me-2"), message],
        color="danger",
        className="mb-2",
    )
    return html.Div(alert)


# Export the layout function and callback registration
__all__ = ["layout", "register_analytics_callbacks"]
