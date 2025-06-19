# pages/deep_analytics.py - UPDATED: Now uses Dependency Injection
"""
Deep Analytics page with Dependency Injection
UPDATED: Services now injected instead of imported directly
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, State, no_update
from flask_babel import lazy_gettext as _l
from core.auth import role_required
import dash_bootstrap_components as dbc
from typing import List, Dict, Any, Optional, Tuple, Union
from core.plugins.decorators import safe_callback
import logging

logger = logging.getLogger(__name__)

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
        return str(html.Div(_l("File uploader not available")))

    def create_data_preview(*args, **kwargs):
        return str(html.Div(_l("Data preview not available")))

    def create_analytics_charts(*args, **kwargs):
        return str(html.Div(_l("Charts not available")))

    def create_summary_cards(*args, **kwargs):
        return str(html.Div(_l("Summary cards not available")))

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
    layout_container = dbc.Container(
        [
            # Page header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1(
                                _l("🔍 Deep Analytics"), className="text-primary mb-0"
                            ),
                            html.P(
                                _l(
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
    return layout_container


def register_analytics_callbacks(app, container=None):
    """Register analytics page callbacks using the JSON plugin"""

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
    def process_uploaded_files_with_plugin(
        contents_list: Optional[Union[str, List[str]]],
        filename_list: Optional[Union[str, List[str]]],
    ) -> Tuple[List[html.Div], Dict[str, Any], List[html.Div]]:
        """Process uploaded files using the JSON plugin for safe serialization"""

        # Get the JSON plugin from the app
        json_plugin = getattr(app, "_yosai_json_plugin", None)

        if json_plugin is None:
            logger.warning("JSON plugin not available, using basic handling")

        try:
            if contents_list is None:
                empty_status = [html.Div("No files uploaded.")]
                return _safe_return(empty_status, {}, [], json_plugin)

            # Ensure we have lists
            if isinstance(contents_list, str):
                contents_list = [contents_list]
            if isinstance(filename_list, str):
                filename_list = [filename_list]

            upload_status = []
            stored_data = {}
            results_components = []

            for i, (contents, filename) in enumerate(zip(contents_list, filename_list)):
                try:
                    # Process the file
                    df = FileProcessor.process_file_content(contents, filename)

                    if df is not None:
                        # Validate the data
                        is_valid, message, suggestions = (
                            FileProcessor.validate_dataframe(df)
                        )

                        if is_valid:
                            # Use JSON plugin to safely store data
                            if json_plugin and json_plugin.serialization_service:
                                # Use plugin's sanitization
                                safe_df_data = json_plugin.serialization_service.sanitize_for_transport(
                                    df
                                )
                                stored_data[f"file_{i}"] = safe_df_data

                                # Generate and sanitize analytics
                                try:
                                    analytics_data = (
                                        AnalyticsGenerator.generate_analytics(df)
                                    )
                                    safe_analytics = json_plugin.serialization_service.sanitize_for_transport(
                                        analytics_data
                                    )
                                    stored_data[f"analytics_{i}"] = safe_analytics
                                except Exception as analytics_error:
                                    stored_data[f"analytics_{i}"] = {
                                        "error": f"Analytics generation failed: {str(analytics_error)}"
                                    }
                            else:
                                # Fallback: basic safe storage
                                stored_data[f"file_{i}"] = {
                                    "filename": str(filename),
                                    "shape": df.shape,
                                    "columns": [str(col) for col in df.columns],
                                    "sample_data": df.head(10).to_dict("records"),
                                    "dtypes": {
                                        str(col): str(dtype)
                                        for col, dtype in df.dtypes.items()
                                    },
                                }

                            # Create UI components
                            try:
                                preview_component = create_data_preview(
                                    df, f"preview-{i}"
                                )
                                charts_component = create_analytics_charts(
                                    df, f"charts-{i}"
                                )
                                summary_component = create_summary_cards(
                                    df, f"summary-{i}"
                                )

                                results_components.extend(
                                    [
                                        html.H4(
                                            f"📊 Analysis: {str(filename)}",
                                            className="mt-4",
                                        ),
                                        summary_component,
                                        preview_component,
                                        charts_component,
                                        html.Hr(),
                                    ]
                                )
                            except Exception as component_error:
                                results_components.append(
                                    html.Div(
                                        [
                                            html.H4(
                                                f"📊 Analysis: {str(filename)}",
                                                className="mt-4",
                                            ),
                                            dbc.Alert(
                                                f"Component error: {str(component_error)}",
                                                color="warning",
                                            ),
                                        ]
                                    )
                                )

                            upload_status.append(
                                html.Div(
                                    [
                                        html.I(
                                            className="fas fa-check-circle text-success me-2"
                                        ),
                                        f"✅ {str(filename)} processed successfully",
                                    ],
                                    className="alert alert-success",
                                )
                            )

                        else:
                            upload_status.append(
                                html.Div(
                                    [
                                        html.I(
                                            className="fas fa-exclamation-triangle text-warning me-2"
                                        ),
                                        f"⚠️ {str(filename)}: {str(message)}",
                                    ],
                                    className="alert alert-warning",
                                )
                            )
                    else:
                        upload_status.append(
                            html.Div(
                                [
                                    html.I(
                                        className="fas fa-times-circle text-danger me-2"
                                    ),
                                    f"❌ {str(filename)}: Could not process file",
                                ],
                                className="alert alert-danger",
                            )
                        )

                except Exception as file_error:
                    upload_status.append(
                        html.Div(
                            [
                                html.I(
                                    className="fas fa-times-circle text-danger me-2"
                                ),
                                f"❌ {str(filename)}: {str(file_error)}",
                            ],
                            className="alert alert-danger",
                        )
                    )

            # Return safely using plugin
            return _safe_return(
                upload_status, stored_data, results_components, json_plugin
            )

        except Exception as e:
            error_message = f"Error processing files: {str(e)}"
            logger.error(error_message)

            error_status = [
                html.Div(
                    [
                        html.I(className="fas fa-times-circle text-danger me-2"),
                        f"❌ {error_message}",
                    ],
                    className="alert alert-danger",
                )
            ]

            return _safe_return(error_status, {}, [], json_plugin)


def _safe_return(upload_status, stored_data, results_components, json_plugin):
    """Safely return callback data using JSON plugin if available"""
    if json_plugin and json_plugin.serialization_service:
        # Use plugin's sanitization for all return values
        safe_upload_status = json_plugin.serialization_service.sanitize_for_transport(
            upload_status
        )
        safe_stored_data = json_plugin.serialization_service.sanitize_for_transport(
            stored_data
        )
        safe_results = json_plugin.serialization_service.sanitize_for_transport(
            results_components
        )
        return safe_upload_status, safe_stored_data, safe_results
    else:
        # Fallback: basic conversion to ensure JSON safety
        def basic_sanitize(obj):
            if hasattr(obj, "__class__") and "LazyString" in str(obj.__class__):
                return str(obj)
            if isinstance(obj, dict):
                return {str(k): basic_sanitize(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [basic_sanitize(item) for item in obj]
            return obj

        return (
            basic_sanitize(upload_status),
            basic_sanitize(stored_data),
            basic_sanitize(results_components),
        )


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
