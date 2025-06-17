# pages/deep_analytics.py - UPDATED: Now uses Dependency Injection
"""
Deep Analytics page with Dependency Injection
UPDATED: Services now injected instead of imported directly
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, State, no_update
from core.auth import role_required
import dash_bootstrap_components as dbc
from typing import List, Dict, Any, Optional, Tuple, Union

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

    # Create fallback functions (same as before)
    def create_file_uploader(*args, **kwargs):
        return html.Div("File uploader not available")

    def create_data_preview(*args, **kwargs):
        return html.Div("Data preview not available")

    def create_analytics_charts(*args, **kwargs):
        return html.Div("Charts not available")

    def create_summary_cards(*args, **kwargs):
        return html.Div("Summary cards not available")

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
    """Deep Analytics page layout - same as before"""
    return dbc.Container(
        [
            # Page header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1("🔍 Deep Analytics", className="text-primary mb-0"),
                            html.P(
                                "Advanced data analysis and visualization for security intelligence",
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
    @role_required("admin")
    def process_uploaded_files(
        contents_list: Optional[Union[str, List[str]]],
        filename_list: Optional[Union[str, List[str]]],
    ) -> Tuple[List[html.Div], Dict[str, Any], List[html.Div]]:
        """Process uploaded files with Dependency Injection"""

        # Early return with proper types if no content
        if not contents_list or not filename_list:
            return [], {}, []

        # Ensure inputs are lists
        if isinstance(contents_list, str):
            contents_list = [contents_list]
        if isinstance(filename_list, str):
            filename_list = [filename_list]

        # Get services from DI container
        analytics_service = None
        file_processor = None

        if container is not None:
            try:
                analytics_service = container.get("analytics_service")
                file_processor = container.get("file_processor")
            except Exception as e:
                print(f"Warning: Could not get services from container: {e}")

        # Fallback to static classes if DI not available
        if file_processor is None:
            file_processor = FileProcessor

        status_messages: List[html.Div] = []
        all_data: List[Dict[str, Any]] = []

        # Process each uploaded file
        for contents, filename in zip(contents_list, filename_list):
            try:
                # Use the injected or fallback FileProcessor
                if hasattr(file_processor, "process_file_content"):
                    df = file_processor.process_file_content(contents, filename)
                else:
                    df = FileProcessor.process_file_content(contents, filename)

                if df is None:
                    status_messages.append(
                        _create_error_alert(f"Unsupported file type: {filename}")
                    )
                    continue

                valid, alerts, suggestions = _validate_file(
                    file_processor, df, filename
                )
                status_messages.extend(alerts)
                if not valid:
                    continue

                # Store processed data
                all_data.append(
                    {
                        "filename": filename,
                        "data": df.to_dict("records"),
                        "columns": list(df.columns),
                        "rows": len(df),
                        "suggestions": suggestions,
                    }
                )

            except Exception as e:
                status_messages.append(
                    _create_error_alert(f"Error processing {filename}: {str(e)}")
                )

        # Generate analytics components
        analytics_components: List[html.Div] = []

        if all_data:
            combined_df = _combine_uploaded_data(all_data)

            if not combined_df.empty:
                analytics_data = _generate_analytics_data(
                    analytics_service, combined_df, len(all_data)
                )

                analytics_components = [
                    html.Div(html.Hr()),
                    html.Div([html.H3("📊 Analytics Results", className="mb-4")]),
                    html.Div(create_summary_cards(analytics_data)),
                    html.Div(
                        create_data_preview(
                            combined_df, f"Combined Data ({len(all_data)} files)"
                        )
                    ),
                    html.Div([html.H4("📈 Visualizations", className="mb-3")]),
                    html.Div(create_analytics_charts(analytics_data)),
                ]

        return status_messages, {"files": all_data}, analytics_components


# Helper functions (same as before)


def _validate_file(
    file_processor: Any, df: pd.DataFrame, filename: str
) -> Tuple[bool, List[html.Div], List[str]]:
    """Validate an uploaded DataFrame and build alert messages.

    Parameters
    ----------
    file_processor : Any
        Processor instance providing ``validate_dataframe``.
    df : pd.DataFrame
        Parsed DataFrame from the uploaded file.
    filename : str
        Name of the uploaded file.

    Returns
    -------
    Tuple[bool, List[html.Div], List[str]]
        ``valid`` flag, list of alert ``html.Div`` messages and suggestions.
    """

    if hasattr(file_processor, "validate_dataframe"):
        valid, message, suggestions = file_processor.validate_dataframe(df)
    else:
        valid, message, suggestions = FileProcessor.validate_dataframe(df)

    alerts: List[html.Div] = []
    if not valid:
        alert_div = _create_warning_alert(f"{filename}: {message}")
        if suggestions:
            suggestions_list = html.Ul([html.Li(s) for s in suggestions])
            alerts.append(html.Div([alert_div, suggestions_list]))
        else:
            alerts.append(alert_div)
    else:
        alerts.append(
            _create_success_alert(
                f"✅ Successfully loaded {filename}: {len(df):,} rows × {len(df.columns)} columns"
            )
        )

    return valid, alerts, suggestions


def _generate_analytics_data(
    analytics_service: Any, combined_df: pd.DataFrame, num_files: int
) -> Dict[str, Any]:
    """Generate analytics data using DI service or fallback.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing analytics results.
    """

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
