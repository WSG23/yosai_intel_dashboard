#!/usr/bin/env python3
"""
COMPLETE DEEP ANALYTICS FIX
Fixes all method and import errors
Replace the broken functions in pages/deep_analytics.py
"""

# =============================================================================
# SECTION 1: CORRECTED IMPORTS (Replace at top of pages/deep_analytics.py)
# =============================================================================

import logging
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

# Dash core imports
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

# Internal service imports with CORRECTED paths
try:
    from services.analytics_service import AnalyticsService

    ANALYTICS_SERVICE_AVAILABLE = True
except ImportError:
    ANALYTICS_SERVICE_AVAILABLE = False

try:
    from components.column_verification import get_ai_suggestions_for_file

    AI_SUGGESTIONS_AVAILABLE = True
except ImportError:
    AI_SUGGESTIONS_AVAILABLE = False

# Logger setup
logger = logging.getLogger(__name__)

# =============================================================================
# SECTION 2: SAFE SERVICE UTILITIES
# Add these utility functions to pages/deep_analytics.py
# =============================================================================


def get_analytics_service_safe() -> Optional[AnalyticsService]:
    """Safely get analytics service instance"""
    try:
        if ANALYTICS_SERVICE_AVAILABLE:
            return AnalyticsService()
        return None
    except Exception as e:
        logger.warning(f"Analytics service unavailable: {e}")
        return None


def get_data_source_options_safe() -> List[Dict[str, str]]:
    """CORRECTED - Get available data sources with proper imports"""
    options = []

    try:
        # CORRECTED IMPORT PATH - Use pages.file_upload not components.file_upload
        from pages.file_upload import get_uploaded_data

        uploaded_files = get_uploaded_data()

        print(f"🔍 Found {len(uploaded_files)} uploaded files")

        for filename, df in uploaded_files.items():
            print(f"   📄 {filename}: {len(df):,} rows × {len(df.columns)} columns")

            # Check if AI suggestions are available for this file
            has_suggestions = False
            if AI_SUGGESTIONS_AVAILABLE:
                try:
                    suggestions = get_ai_suggestions_for_file(df, filename)
                    has_suggestions = bool(
                        suggestions
                        and any(s.get("field") for s in suggestions.values())
                    )
                    print(
                        f"      🤖 AI suggestions: {'Available' if has_suggestions else 'None'}"
                    )
                except Exception as e:
                    print(f"      ⚠️ AI suggestions failed: {e}")
                    pass

            suggestion_indicator = " 🤖" if has_suggestions else " 📄"
            options.append(
                {
                    "label": f"{filename}{suggestion_indicator}",
                    "value": f"upload:{filename}",
                }
            )
    except ImportError as e:
        print(f"❌ Import error: {e}")
        options.append({"label": "⚠️ File upload module not available", "value": "none"})
    except Exception as e:
        print(f"❌ Error getting uploaded files: {e}")
        options.append({"label": f"⚠️ Error: {str(e)}", "value": "none"})

    # Add service-based sources if available - CORRECTED method name
    try:
        service = get_analytics_service_safe()
        if service:
            # Use the actual method name from AnalyticsService
            service_sources = (
                service.get_data_source_options()
            )  # This is the correct method name
            for source_dict in service_sources:
                options.append(
                    {
                        "label": f"🔗 {source_dict.get('label', 'Unknown')}",
                        "value": f"service:{source_dict.get('value', 'unknown')}",
                    }
                )
    except Exception as e:
        print(f"⚠️ Service sources unavailable: {e}")

    if not options:
        options.append(
            {"label": "No data sources available - Upload files first", "value": "none"}
        )

    print(f"✅ Generated {len(options)} data source options")
    return options


def get_analysis_type_options() -> List[Dict[str, str]]:
    """Get available analysis types including suggests analysis"""
    return [
        {"label": "🔒 Security Patterns", "value": "security"},
        {"label": "📈 Access Trends", "value": "trends"},
        {"label": "👤 User Behavior", "value": "behavior"},
        {"label": "🚨 Anomaly Detection", "value": "anomaly"},
        {"label": "🤖 AI Column Suggestions", "value": "suggests"},
        {"label": "📊 Data Quality", "value": "quality"},
    ]


# =============================================================================
# SECTION 3: SUGGESTS ANALYSIS PROCESSOR
# Add this new function to handle suggests display
# =============================================================================


def process_suggests_analysis(data_source: str) -> Dict[str, Any]:
    """Process AI suggestions analysis for the selected data source"""
    try:
        print(f"🔍 Processing suggests analysis for: {data_source}")

        if not data_source or data_source == "none":
            return {"error": "No data source selected"}

        # Handle BOTH upload formats
        if data_source.startswith("upload:") or data_source == "service:uploaded":

            if data_source.startswith("upload:"):
                filename = data_source.replace("upload:", "")
            else:
                # Handle service:uploaded - use first available file
                filename = None

            from pages.file_upload import get_uploaded_data

            uploaded_files = get_uploaded_data()

            if not uploaded_files:
                return {"error": "No uploaded files found"}

            # If no specific filename, use the first available file
            if filename is None or filename not in uploaded_files:
                filename = list(uploaded_files.keys())[0]

            df = uploaded_files[filename]

            # Get AI suggestions
            if AI_SUGGESTIONS_AVAILABLE:
                try:
                    suggestions = get_ai_suggestions_for_file(df, filename)

                    processed_suggestions = []
                    total_confidence = 0
                    confident_mappings = 0

                    for column, suggestion in suggestions.items():
                        field = suggestion.get("field", "")
                        confidence = suggestion.get("confidence", 0.0)

                        status = (
                            "🟢 High"
                            if confidence >= 0.7
                            else "🟡 Medium" if confidence >= 0.4 else "🔴 Low"
                        )

                        try:
                            sample_data = (
                                df[column].dropna().head(3).astype(str).tolist()
                            )
                        except Exception:
                            sample_data = ["N/A"]

                        processed_suggestions.append(
                            {
                                "column": column,
                                "suggested_field": field if field else "No suggestion",
                                "confidence": confidence,
                                "status": status,
                                "sample_data": sample_data,
                            }
                        )

                        total_confidence += confidence
                        if confidence >= 0.6:
                            confident_mappings += 1

                    avg_confidence = (
                        total_confidence / len(suggestions) if suggestions else 0
                    )

                    try:
                        data_preview = df.head(5).to_dict("records")
                    except Exception:
                        data_preview = []

                    return {
                        "filename": filename,
                        "total_columns": len(df.columns),
                        "total_rows": len(df),
                        "suggestions": processed_suggestions,
                        "avg_confidence": avg_confidence,
                        "confident_mappings": confident_mappings,
                        "data_preview": data_preview,
                        "column_names": list(df.columns),
                    }

                except Exception as e:
                    return {"error": f"AI suggestions failed: {str(e)}"}
            else:
                return {"error": "AI suggestions service not available"}
        else:
            return {
                "error": f"Suggests analysis not available for data source: {data_source}"
            }

    except Exception as e:
        return {"error": f"Failed to process suggests: {str(e)}"}


# =============================================================================
# SECTION 4: SUGGESTS DISPLAY COMPONENTS
# Add these functions to create suggests UI components
# =============================================================================


def create_suggests_display(suggests_data: Dict[str, Any]) -> html.Div:
    """Create suggests analysis display components (working version)"""
    if "error" in suggests_data:
        return dbc.Alert(f"Error: {suggests_data['error']}", color="danger")

    try:
        filename = suggests_data.get("filename", "Unknown")
        suggestions = suggests_data.get("suggestions", [])
        avg_confidence = suggests_data.get("avg_confidence", 0)
        confident_mappings = suggests_data.get("confident_mappings", 0)
        total_columns = suggests_data.get("total_columns", 0)
        total_rows = suggests_data.get("total_rows", 0)

        # Summary card
        summary_card = dbc.Card(
            [
                dbc.CardHeader(
                    [html.H5(f"🤖 AI Column Mapping Analysis - {filename}")]
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H6("Dataset Info"),
                                        html.P(f"File: {filename}"),
                                        html.P(f"Rows: {total_rows:,}"),
                                        html.P(f"Columns: {total_columns}"),
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        html.H6("Overall Confidence"),
                                        dbc.Progress(
                                            value=avg_confidence * 100,
                                            label=f"{avg_confidence:.1%}",
                                            color=(
                                                "success"
                                                if avg_confidence >= 0.7
                                                else (
                                                    "warning"
                                                    if avg_confidence >= 0.4
                                                    else "danger"
                                                )
                                            ),
                                        ),
                                    ],
                                    width=4,
                                ),
                                dbc.Col(
                                    [
                                        html.H6("Confident Mappings"),
                                        html.H3(
                                            f"{confident_mappings}/{total_columns}",
                                            className=(
                                                "text-success"
                                                if confident_mappings
                                                >= total_columns * 0.7
                                                else "text-warning"
                                            ),
                                        ),
                                    ],
                                    width=4,
                                ),
                            ]
                        )
                    ]
                ),
            ],
            className="mb-3",
        )

        # Suggestions table
        if suggestions:
            table_rows = []
            for suggestion in suggestions:
                confidence = suggestion["confidence"]

                table_rows.append(
                    html.Tr(
                        [
                            html.Td(suggestion["column"]),
                            html.Td(suggestion["suggested_field"]),
                            html.Td(
                                [
                                    dbc.Progress(
                                        value=confidence * 100,
                                        label=f"{confidence:.1%}",
                                        size="sm",
                                        color=(
                                            "success"
                                            if confidence >= 0.7
                                            else (
                                                "warning"
                                                if confidence >= 0.4
                                                else "danger"
                                            )
                                        ),
                                    )
                                ]
                            ),
                            html.Td(suggestion["status"]),
                            html.Td(
                                html.Small(
                                    str(suggestion["sample_data"][:2]),
                                    className="text-muted",
                                )
                            ),
                        ]
                    )
                )

            suggestions_table = dbc.Card(
                [
                    dbc.CardHeader([html.H6("📋 Column Mapping Suggestions")]),
                    dbc.CardBody(
                        [
                            dbc.Table(
                                [
                                    html.Thead(
                                        [
                                            html.Tr(
                                                [
                                                    html.Th("Column Name"),
                                                    html.Th("Suggested Field"),
                                                    html.Th("Confidence"),
                                                    html.Th("Status"),
                                                    html.Th("Sample Data"),
                                                ]
                                            )
                                        ]
                                    ),
                                    html.Tbody(table_rows),
                                ],
                                responsive=True,
                                striped=True,
                            )
                        ]
                    ),
                ],
                className="mb-3",
            )
        else:
            suggestions_table = dbc.Alert("No suggestions available", color="warning")

        return html.Div([summary_card, suggestions_table])

    except Exception as e:
        logger.error(f"Error creating suggests display: {e}")
        return dbc.Alert(f"Error creating display: {str(e)}", color="danger")


# =============================================================================
# SECTION 5: LAYOUT FUNCTION REPLACEMENT
# COMPLETELY REPLACE the layout() function in pages/deep_analytics.py
# =============================================================================


def layout():
    """
    COMPLETE REPLACEMENT for the layout function in pages/deep_analytics.py

    INTEGRATION STEPS:
    1. Find the existing layout() function in pages/deep_analytics.py
    2. Replace the ENTIRE function with this code
    3. Keep the function name as 'layout'
    """
    try:
        # Header section
        header = dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("🔍 Deep Analytics", className="text-primary"),
                        html.P(
                            "Advanced data analysis with AI-powered column mapping suggestions",
                            className="lead text-muted",
                        ),
                        dbc.Alert(
                            "✅ UI components loaded successfully",
                            color="success",
                            dismissable=True,
                            id="status-alert",
                        ),
                    ]
                )
            ],
            className="mb-4",
        )

        # Configuration section
        config_card = dbc.Card(
            [
                dbc.CardHeader([html.H5("⚙️ Analysis Configuration")]),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Label("Data Source", className="fw-bold"),
                                        dcc.Dropdown(
                                            id="analytics-data-source",
                                            options=get_data_source_options_safe(),
                                            placeholder="Select data source...",
                                            value=None,
                                        ),
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        html.Label(
                                            "Analysis Type", className="fw-bold"
                                        ),
                                        dcc.Dropdown(
                                            id="analytics-type",
                                            options=get_analysis_type_options(),
                                            value="suggests",
                                            placeholder="Select analysis type...",
                                        ),
                                    ],
                                    width=6,
                                ),
                            ],
                            className="mb-3",
                        ),
                        html.Hr(),
                        dbc.ButtonGroup(
                            [
                                dbc.Button(
                                    "🚀 Generate Analytics",
                                    id="generate-analytics-btn",
                                    color="primary",
                                    size="lg",
                                ),
                                dbc.Button(
                                    "🔄 Refresh Data Sources",
                                    id="refresh-sources-btn",
                                    color="outline-secondary",
                                    size="lg",
                                ),
                            ]
                        ),
                    ]
                ),
            ],
            className="mb-4",
        )

        # Results display area
        results_area = html.Div(
            id="analytics-display-area",
            children=[
                dbc.Alert(
                    [
                        html.H6("👆 Get Started"),
                        html.P(
                            "1. Select a data source (files with 🤖 have AI suggestions)"
                        ),
                        html.P(
                            "2. Choose 'AI Column Suggestions' to see mapping analysis"
                        ),
                        html.P("3. Click 'Generate Analytics' to begin"),
                    ],
                    color="info",
                )
            ],
        )

        # Hidden stores and triggers
        stores = [
            dcc.Store(id="analytics-results-store", data={}),
            dcc.Store(id="service-health-store", data={}),
            html.Div(id="hidden-trigger", style={"display": "none"}),
        ]

        # Complete layout
        return dbc.Container([header, config_card, results_area] + stores, fluid=True)

    except Exception as e:
        logger.error(f"Critical error creating layout: {e}")
        return dbc.Container(
            [
                dbc.Alert(
                    [
                        html.H4("⚠️ Page Loading Error"),
                        html.P(f"Error: {str(e)}"),
                        html.P("Please check imports and dependencies."),
                    ],
                    color="danger",
                )
            ]
        )


# =============================================================================
# SECTION 6: CONSOLIDATED CALLBACKS
# REPLACE the existing callbacks in pages/deep_analytics.py with these
# =============================================================================


@callback(
    Output("analytics-display-area", "children"),
    [Input("generate-analytics-btn", "n_clicks")],
    [State("analytics-data-source", "value"), State("analytics-type", "value")],
    prevent_initial_call=True,
)
def corrected_analytics_callback(n_clicks, data_source, analysis_type):
    """
    CORRECTED CALLBACK - Replace the existing analytics callback

    INTEGRATION INSTRUCTIONS:
    1. Find the existing callback that updates "analytics-display-area"
    2. Replace it with this entire callback function
    3. Keep the @callback decorator
    """
    if not n_clicks or not data_source or data_source == "none":
        return dbc.Alert("Please select a valid data source", color="warning")

    try:
        print(f"🚀 Starting analysis: {analysis_type} for {data_source}")

        # Handle suggests analysis (this works)
        if analysis_type == "suggests":
            suggests_data = process_suggests_analysis(data_source)
            return create_suggests_display(suggests_data)

        # Handle data quality analysis (corrected)
        elif analysis_type == "quality":
            return create_data_quality_display_corrected(data_source)

        # Handle other analysis types with corrected service calls
        elif analysis_type in ["security", "trends", "behavior", "anomaly"]:
            try:
                # Use the corrected service analysis function
                results = analyze_data_with_service(data_source, analysis_type)

                if "error" in results:
                    return dbc.Alert(
                        f"Analysis failed: {results['error']}", color="danger"
                    )

                return create_analysis_results_display(results, analysis_type)

            except Exception as e:
                print(f"❌ Analysis failed: {e}")
                return dbc.Alert(f"Analysis failed: {str(e)}", color="danger")

        else:
            return dbc.Alert(
                f"Analysis type '{analysis_type}' not supported", color="warning"
            )

    except Exception as e:
        logger.error(f"Analytics callback error: {e}")
        return dbc.Alert(f"Error: {str(e)}", color="danger")


@callback(
    Output("analytics-data-source", "options"),
    Input("refresh-sources-btn", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_data_sources_callback(n_clicks):
    """Refresh data sources when button clicked"""
    if n_clicks:
        return get_data_source_options_safe()
    return get_data_source_options_safe()


@callback(
    Output("status-alert", "children"),
    Input("hidden-trigger", "children"),
    prevent_initial_call=False,
)
def update_status_alert(trigger):
    """Update status based on service health"""
    try:
        service = get_analytics_service_safe()
        suggests_available = AI_SUGGESTIONS_AVAILABLE

        if service and suggests_available:
            return "✅ All services available - Full functionality enabled"
        elif suggests_available:
            return "⚠️ Analytics service limited - AI suggestions available"
        elif service:
            return "⚠️ AI suggestions unavailable - Analytics service available"
        else:
            return "🔄 Running in limited mode - Some features may be unavailable"
    except Exception:
        return "❌ Service status unknown"


# =============================================================================
# SECTION 7: HELPER DISPLAY FUNCTIONS
# Add these helper functions for non-suggests analysis types
# =============================================================================


def analyze_data_with_service(data_source: str, analysis_type: str) -> Dict[str, Any]:
    """Use actual AnalyticsService methods"""
    try:
        service = get_analytics_service_safe()
        if not service:
            return {"error": "Analytics service not available"}

        # Convert data source format
        if data_source.startswith("upload:") or data_source == "service:uploaded":
            source_name = "uploaded"
        elif data_source.startswith("service:"):
            source_name = data_source.replace("service:", "")
        else:
            source_name = data_source

        # Use the actual method
        analytics_results = service.get_analytics_by_source(source_name)

        if analytics_results.get("status") == "error":
            return {"error": analytics_results.get("message", "Unknown error")}

        # Fix success rate calculation
        total_events = analytics_results.get("total_events", 0)
        success_rate = analytics_results.get("success_rate", 0)

        # If success rate is 0, try to calculate it
        if success_rate == 0 and "successful_events" in analytics_results:
            successful_events = analytics_results.get("successful_events", 0)
            if total_events > 0:
                success_rate = successful_events / total_events

        return {
            "analysis_type": analysis_type,
            "data_source": data_source,
            "total_events": total_events,
            "unique_users": analytics_results.get("unique_users", 0),
            "unique_doors": analytics_results.get("unique_doors", 0),
            "success_rate": success_rate,
            "date_range": analytics_results.get("date_range", {}),
            "raw_results": analytics_results,
        }

    except Exception as e:
        return {"error": f"Service analysis failed: {str(e)}"}


def create_data_quality_display_corrected(data_source: str) -> html.Div:
    """Data quality analysis with proper imports"""
    try:
        # Handle BOTH upload formats
        if data_source.startswith("upload:") or data_source == "service:uploaded":

            if data_source.startswith("upload:"):
                filename = data_source.replace("upload:", "")
            else:
                filename = None

            from pages.file_upload import get_uploaded_data

            uploaded_files = get_uploaded_data()

            if not uploaded_files:
                return dbc.Alert("No uploaded files found", color="warning")

            # If no specific filename, use the first available file
            if filename is None or filename not in uploaded_files:
                filename = list(uploaded_files.keys())[0]

            if filename in uploaded_files:
                df = uploaded_files[filename]

                total_rows = len(df)
                total_cols = len(df.columns)
                missing_values = df.isnull().sum().sum()
                duplicate_rows = df.duplicated().sum()

                quality_score = max(
                    0,
                    100
                    - (missing_values / (total_rows * total_cols) * 100)
                    - (duplicate_rows / total_rows * 10),
                )

                return dbc.Card(
                    [
                        dbc.CardHeader(
                            [html.H5(f"📊 Data Quality Analysis - {filename}")]
                        ),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.H6("Dataset Overview"),
                                                html.P(f"File: {filename}"),
                                                html.P(f"Rows: {total_rows:,}"),
                                                html.P(f"Columns: {total_cols}"),
                                                html.P(
                                                    f"Missing values: {missing_values:,}"
                                                ),
                                                html.P(
                                                    f"Duplicate rows: {duplicate_rows:,}"
                                                ),
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            [
                                                html.H6("Quality Score"),
                                                dbc.Progress(
                                                    value=quality_score,
                                                    label=f"{quality_score:.1f}%",
                                                    color=(
                                                        "success"
                                                        if quality_score >= 80
                                                        else (
                                                            "warning"
                                                            if quality_score >= 60
                                                            else "danger"
                                                        )
                                                    ),
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ]
                                )
                            ]
                        ),
                    ]
                )

        return dbc.Alert(
            "Data quality analysis only available for uploaded files", color="info"
        )
    except Exception as e:
        return dbc.Alert(f"Quality analysis error: {str(e)}", color="danger")


def create_analysis_results_display(
    results: Dict[str, Any], analysis_type: str
) -> html.Div:
    """Create display for standard analysis results"""
    try:
        total_events = results.get("total_events", 0)
        unique_users = results.get("unique_users", 0)
        unique_doors = results.get("unique_doors", 0)
        success_rate = results.get("success_rate", 0)

        return dbc.Card(
            [
                dbc.CardHeader(
                    [html.H5(f"📊 {analysis_type.title()} Analysis Results")]
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.H6("Summary Statistics"),
                                        html.P(f"Total Events: {total_events:,}"),
                                        html.P(f"Unique Users: {unique_users:,}"),
                                        html.P(f"Unique Doors: {unique_doors:,}"),
                                        html.P(f"Success Rate: {success_rate:.1%}"),
                                    ],
                                    width=6,
                                ),
                                dbc.Col(
                                    [
                                        html.H6("Analysis Details"),
                                        html.P(
                                            f"Analysis Type: {analysis_type.title()}"
                                        ),
                                        html.P(
                                            f"Data Source: {results.get('data_source', 'Unknown')}"
                                        ),
                                        html.P(
                                            f"Date Range: {results.get('date_range', {}).get('start', 'Unknown')} to {results.get('date_range', {}).get('end', 'Unknown')}"
                                        ),
                                    ],
                                    width=6,
                                ),
                            ]
                        ),
                        html.Hr(),
                        dbc.Alert(
                            [
                                html.H6("Analysis Complete"),
                                html.P(
                                    f"Successfully processed {total_events:,} events for {analysis_type} analysis."
                                ),
                                html.P(
                                    "Detailed charts and insights would be displayed here in the full implementation."
                                ),
                            ],
                            color="success",
                        ),
                    ]
                ),
            ]
        )
    except Exception as e:
        return dbc.Alert(f"Error displaying results: {str(e)}", color="danger")


def create_limited_analysis_display(data_source: str, analysis_type: str) -> html.Div:
    """Create limited analysis display when service unavailable"""
    return dbc.Card(
        [
            dbc.CardHeader([html.H5(f"⚠️ Limited {analysis_type.title()} Analysis")]),
            dbc.CardBody(
                [
                    dbc.Alert(
                        [
                            html.H6("Service Limitations"),
                            html.P("Full analytics service is not available."),
                            html.P("Basic analysis results would be shown here."),
                        ],
                        color="warning",
                    ),
                    html.P(f"Data source: {data_source}"),
                    html.P(f"Analysis type: {analysis_type}"),
                ]
            ),
        ]
    )


def create_data_quality_display(data_source: str) -> html.Div:
    """Create data quality analysis display"""
    try:
        if data_source.startswith("upload:"):
            filename = data_source.replace("upload:", "")
            from components.file_upload import get_uploaded_data_store

            uploaded_files = get_uploaded_data_store()

            if filename in uploaded_files:
                df = uploaded_files[filename]

                # Basic quality metrics
                total_rows = len(df)
                total_cols = len(df.columns)
                missing_values = df.isnull().sum().sum()
                duplicate_rows = df.duplicated().sum()

                return dbc.Card(
                    [
                        dbc.CardHeader([html.H5("📊 Data Quality Analysis")]),
                        dbc.CardBody(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.H6("Dataset Overview"),
                                                html.P(f"Rows: {total_rows:,}"),
                                                html.P(f"Columns: {total_cols}"),
                                                html.P(
                                                    f"Missing values: {missing_values:,}"
                                                ),
                                                html.P(
                                                    f"Duplicate rows: {duplicate_rows:,}"
                                                ),
                                            ],
                                            width=6,
                                        ),
                                        dbc.Col(
                                            [
                                                html.H6("Quality Score"),
                                                dbc.Progress(
                                                    value=max(
                                                        0,
                                                        100
                                                        - (
                                                            missing_values
                                                            / total_rows
                                                            * 100
                                                        )
                                                        - (
                                                            duplicate_rows
                                                            / total_rows
                                                            * 10
                                                        ),
                                                    ),
                                                    label="Quality",
                                                    color="success",
                                                ),
                                            ],
                                            width=6,
                                        ),
                                    ]
                                )
                            ]
                        ),
                    ]
                )
        return dbc.Alert(
            "Data quality analysis only available for uploaded files", color="info"
        )
    except Exception as e:
        return dbc.Alert(f"Quality analysis error: {str(e)}", color="danger")
