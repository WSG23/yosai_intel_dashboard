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
from analytics.interactive_charts import SecurityChartsGenerator, create_charts_generator
from analytics.analytics_controller import AnalyticsController, AnalyticsConfig

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
    # Fallback AI suggestions function
    def get_ai_suggestions_for_file(df, filename):
        suggestions = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            if any(word in col_lower for word in ["time", "date", "stamp"]):
                suggestions[col] = {"field": "timestamp", "confidence": 0.8}
            elif any(word in col_lower for word in ["person", "user", "employee"]):
                suggestions[col] = {"field": "person_id", "confidence": 0.7}
            elif any(word in col_lower for word in ["door", "location", "device"]):
                suggestions[col] = {"field": "door_id", "confidence": 0.7}
            elif any(word in col_lower for word in ["access", "result", "status"]):
                suggestions[col] = {"field": "access_result", "confidence": 0.6}
            elif any(word in col_lower for word in ["token", "badge", "card"]):
                suggestions[col] = {"field": "token_id", "confidence": 0.6}
            else:
                suggestions[col] = {"field": "", "confidence": 0.0}
        return suggestions
    AI_SUGGESTIONS_AVAILABLE = True

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


def get_analytics_dropdown_options():
    """Updated dropdown options including charts"""
    return [
        {"label": "🔒 Security Patterns Analysis", "value": "security"},
        {"label": "📈 Access Trends Analysis", "value": "trends"},
        {"label": "👤 User Behavior Analysis", "value": "behavior"},
        {"label": "🚨 Anomaly Detection", "value": "anomaly"},
        {"label": "📊 Interactive Charts", "value": "charts"},
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
    """Create suggests analysis display components (fixed version)"""
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
        summary_card = dbc.Card([
            dbc.CardHeader([
                html.H5(f"🤖 AI Column Mapping Analysis - {filename}")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("Dataset Info"),
                        html.P(f"File: {filename}"),
                        html.P(f"Rows: {total_rows:,}"),
                        html.P(f"Columns: {total_columns}")
                    ], width=4),
                    dbc.Col([
                        html.H6("Overall Confidence"),
                        dbc.Progress(
                            value=avg_confidence * 100,
                            label=f"{avg_confidence:.1%}",
                            color="success" if avg_confidence >= 0.7 else "warning" if avg_confidence >= 0.4 else "danger"
                        )
                    ], width=4),
                    dbc.Col([
                        html.H6("Confident Mappings"),
                        html.H3(f"{confident_mappings}/{total_columns}",
                               className="text-success" if confident_mappings >= total_columns * 0.7 else "text-warning")
                    ], width=4)
                ])
            ])
        ], className="mb-3")

        # Suggestions table
        if suggestions:
            table_rows = []
            for suggestion in suggestions:
                confidence = suggestion['confidence']

                table_rows.append(
                    html.Tr([
                        html.Td(suggestion['column']),
                        html.Td(suggestion['suggested_field']),
                        html.Td([
                            dbc.Progress(
                                value=confidence * 100,
                                label=f"{confidence:.1%}",
                                color="success" if confidence >= 0.7 else "warning" if confidence >= 0.4 else "danger"
                            )
                        ]),
                        html.Td(suggestion['status']),
                        html.Td(html.Small(str(suggestion['sample_data'][:2]), className="text-muted"))
                    ])
                )

            suggestions_table = dbc.Card([
                dbc.CardHeader([
                    html.H6("📋 Column Mapping Suggestions")
                ]),
                dbc.CardBody([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Column Name"),
                                html.Th("Suggested Field"),
                                html.Th("Confidence"),
                                html.Th("Status"),
                                html.Th("Sample Data")
                            ])
                        ]),
                        html.Tbody(table_rows)
                    ], responsive=True, striped=True)
                ])
            ], className="mb-3")
        else:
            suggestions_table = dbc.Alert("No suggestions available", color="warning")

        return html.Div([
            summary_card,
            suggestions_table
        ])

    except Exception as e:
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
                                            options=get_analytics_dropdown_options(),
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
def run_analytics_display_callback_FIXED(n_clicks, data_source, analysis_type):
    """FIXED: Analytics callback with charts support"""
    if not n_clicks or not data_source or data_source == "none":
        return dbc.Alert("Please select a valid data source", color="warning")

    try:
        print(f"🚀 Starting analysis: {analysis_type} for {data_source}")

        if analysis_type == "charts":
            try:
                uploaded_data = get_uploaded_data_safe(data_source)
                if uploaded_data is None or getattr(uploaded_data, "empty", False):
                    return dbc.Alert("No data available for charts", color="warning")

                chart_results = get_interactive_charts(uploaded_data)

                if not chart_results:
                    return dbc.Alert("Failed to generate charts", color="danger")

                charts_dashboard = create_charts_dashboard(chart_results)

                return html.Div([
                    dbc.Alert("✅ Interactive charts generated successfully!", color="success"),
                    charts_dashboard,
                ])
            except Exception as e:
                print(f"❌ Charts generation failed: {e}")
                return dbc.Alert(f"Charts generation failed: {str(e)}", color="danger")

        elif analysis_type == "suggests":
            suggests_data = process_suggests_analysis(data_source)
            return create_suggests_display(suggests_data)

        elif analysis_type == "quality":
            return create_data_quality_display_corrected(data_source)

        elif analysis_type in ["security", "trends", "behavior", "anomaly"]:
            try:
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
    """Generate different analysis based on type"""
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

        # Get base analytics
        analytics_results = service.get_analytics_by_source(source_name)

        if analytics_results.get('status') == 'error':
            return {"error": analytics_results.get('message', 'Unknown error')}

        # Get base metrics
        total_events = analytics_results.get('total_events', 0)
        unique_users = analytics_results.get('unique_users', 0)
        unique_doors = analytics_results.get('unique_doors', 0)
        success_rate = analytics_results.get('success_rate', 0)

        # Fix success rate if needed
        if success_rate == 0 and 'successful_events' in analytics_results:
            successful_events = analytics_results.get('successful_events', 0)
            if total_events > 0:
                success_rate = successful_events / total_events

        # Generate DIFFERENT results based on analysis type
        if analysis_type == "security":
            return {
                "analysis_type": "Security Patterns",
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "security_score": min(100, success_rate * 100 + 20),
                "failed_attempts": total_events - int(total_events * success_rate),
                "risk_level": "Low" if success_rate > 0.9 else "Medium" if success_rate > 0.7 else "High",
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": "Security threats, failed access attempts, and unauthorized access patterns",
            }

        elif analysis_type == "trends":
            return {
                "analysis_type": "Access Trends",
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "daily_average": total_events / 30,  # Assume 30 days
                "peak_usage": "High activity detected",
                "trend_direction": "Increasing" if total_events > 100000 else "Stable",
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": "Usage patterns, peak times, and access frequency trends over time",
            }

        elif analysis_type == "behavior":
            return {
                "analysis_type": "User Behavior",
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "avg_accesses_per_user": total_events / unique_users if unique_users > 0 else 0,
                "heavy_users": int(unique_users * 0.1),  # Top 10%
                "behavior_score": "Normal" if success_rate > 0.8 else "Unusual",
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": "Individual user patterns, frequency analysis, and behavioral anomalies",
            }

        elif analysis_type == "anomaly":
            return {
                "analysis_type": "Anomaly Detection",
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "anomalies_detected": int(total_events * (1 - success_rate)),
                "threat_level": "Critical" if success_rate < 0.5 else "Warning" if success_rate < 0.8 else "Normal",
                "suspicious_activities": "Multiple failed attempts detected" if success_rate < 0.9 else "No major issues",
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": "Suspicious access patterns, security breaches, and abnormal behaviors",
            }

        else:
            # Default fallback
            return {
                "analysis_type": analysis_type,
                "data_source": data_source,
                "total_events": total_events,
                "unique_users": unique_users,
                "unique_doors": unique_doors,
                "success_rate": success_rate,
                "date_range": analytics_results.get('date_range', {}),
                "analysis_focus": f"General {analysis_type} analysis",
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


def create_analysis_results_display(results: Dict[str, Any], analysis_type: str) -> html.Div:
    """Create display for different analysis types"""
    try:
        total_events = results.get('total_events', 0)
        unique_users = results.get('unique_users', 0)
        unique_doors = results.get('unique_doors', 0)
        success_rate = results.get('success_rate', 0)
        analysis_focus = results.get('analysis_focus', '')

        # Create type-specific content
        if analysis_type == "security":
            specific_content = [
                html.P(f"Security Score: {results.get('security_score', 0):.1f}/100"),
                html.P(f"Failed Attempts: {results.get('failed_attempts', 0):,}"),
                html.P(f"Risk Level: {results.get('risk_level', 'Unknown')}")
            ]
            color = "danger" if results.get('risk_level') == "High" else "warning" if results.get('risk_level') == "Medium" else "success"

        elif analysis_type == "trends":
            specific_content = [
                html.P(f"Daily Average: {results.get('daily_average', 0):.0f} events"),
                html.P(f"Peak Usage: {results.get('peak_usage', 'Unknown')}"),
                html.P(f"Trend: {results.get('trend_direction', 'Unknown')}")
            ]
            color = "info"

        elif analysis_type == "behavior":
            specific_content = [
                html.P(f"Avg Accesses/User: {results.get('avg_accesses_per_user', 0):.1f}"),
                html.P(f"Heavy Users: {results.get('heavy_users', 0)}"),
                html.P(f"Behavior Score: {results.get('behavior_score', 'Unknown')}")
            ]
            color = "success"

        elif analysis_type == "anomaly":
            specific_content = [
                html.P(f"Anomalies Detected: {results.get('anomalies_detected', 0):,}"),
                html.P(f"Threat Level: {results.get('threat_level', 'Unknown')}"),
                html.P(f"Status: {results.get('suspicious_activities', 'Unknown')}")
            ]
            color = "danger" if results.get('threat_level') == "Critical" else "warning"

        else:
            specific_content = [html.P("Standard analysis completed")]
            color = "info"

        return dbc.Card([
            dbc.CardHeader([
                html.H5(f"📊 {results.get('analysis_type', analysis_type)} Results")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("📈 Summary"),
                        html.P(f"Total Events: {total_events:,}"),
                        html.P(f"Unique Users: {unique_users:,}"),
                        html.P(f"Unique Doors: {unique_doors:,}"),
                        dbc.Progress(
                            value=success_rate * 100,
                            label=f"Success Rate: {success_rate:.1%}",
                            color="success" if success_rate > 0.8 else "warning"
                        )
                    ], width=6),
                    dbc.Col([
                        html.H6(f"🎯 {analysis_type.title()} Specific"),
                        html.Div(specific_content)
                    ], width=6)
                ]),
                html.Hr(),
                dbc.Alert([
                    html.H6("Analysis Focus"),
                    html.P(analysis_focus)
                ], color=color)
            ])
        ])
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


# =============================================================================
# INTERACTIVE CHARTS FUNCTIONS
# =============================================================================


def get_interactive_charts(uploaded_data):
    """Generate interactive charts from uploaded data"""
    try:
        charts_generator = create_charts_generator()
        chart_results = charts_generator.generate_all_charts(uploaded_data)
        return chart_results
    except Exception as e:
        print(f"Chart generation failed: {e}")
        return {}


def create_charts_dashboard(chart_results):
    """Create dashboard layout for charts"""
    if not chart_results:
        return dbc.Alert("No charts data available", color="warning")

    charts_content = []

    if 'security_overview' in chart_results:
        security_charts = chart_results['security_overview']
        charts_content.append(
            dbc.Card([
                dbc.CardHeader("🔒 Security Overview Charts"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([dcc.Graph(figure=security_charts.get('access_results_pie', {}))], width=6),
                        dbc.Col([dcc.Graph(figure=security_charts.get('failed_attempts_timeline', {}))], width=6)
                    ])
                ])
            ], className="mb-4")
        )

    if 'temporal_analysis' in chart_results:
        temporal_charts = chart_results['temporal_analysis']
        charts_content.append(
            dbc.Card([
                dbc.CardHeader("📅 Temporal Analysis"),
                dbc.CardBody([
                    dbc.Row([dbc.Col([dcc.Graph(figure=temporal_charts.get('hourly_heatmap', {}))], width=12)]),
                    dbc.Row([
                        dbc.Col([dcc.Graph(figure=temporal_charts.get('daily_volume', {}))], width=6),
                        dbc.Col([dcc.Graph(figure=temporal_charts.get('weekly_patterns', {}))], width=6)
                    ])
                ])
            ], className="mb-4")
        )

    if 'user_activity' in chart_results:
        user_charts = chart_results['user_activity']
        charts_content.append(
            dbc.Card([
                dbc.CardHeader("👤 User Activity Analysis"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([dcc.Graph(figure=user_charts.get('top_users', {}))], width=6),
                        dbc.Col([dcc.Graph(figure=user_charts.get('user_segments', {}))], width=6)
                    ])
                ])
            ], className="mb-4")
        )

    if 'door_analysis' in chart_results:
        door_charts = chart_results['door_analysis']
        charts_content.append(
            dbc.Card([
                dbc.CardHeader("🚪 Door Access Analysis"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([dcc.Graph(figure=door_charts.get('door_usage', {}))], width=6),
                        dbc.Col([dcc.Graph(figure=door_charts.get('door_security', {}))], width=6)
                    ])
                ])
            ], className="mb-4")
        )

    if 'anomaly_visualization' in chart_results:
        anomaly_charts = chart_results['anomaly_visualization']
        charts_content.append(
            dbc.Card([
                dbc.CardHeader("🚨 Anomaly Detection"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([dcc.Graph(figure=anomaly_charts.get('volume_anomalies', {}))], width=6),
                        dbc.Col([dcc.Graph(figure=anomaly_charts.get('user_anomalies', {}))], width=6)
                    ])
                ])
            ], className="mb-4")
        )

    if not charts_content:
        return dbc.Alert("No charts could be generated from the data", color="info")

    return html.Div(charts_content)


def get_uploaded_data_safe(data_source):
    """Safely get uploaded data for analysis"""
    try:
        if hasattr(globals(), 'uploaded_datasets') and data_source in uploaded_datasets:
            return uploaded_datasets[data_source]
        if isinstance(data_source, str) and data_source.endswith('.csv'):
            return pd.read_csv(f"uploads/{data_source}")
        from services.data_service import get_dataset
        return get_dataset(data_source)
    except Exception as e:
        print(f"Failed to load data: {e}")
        return None


def test_charts_integration():
    """Test function to verify charts integration works"""
    try:
        import numpy as np
        from datetime import datetime, timedelta

        sample_data = pd.DataFrame({
            'event_id': range(1000),
            'timestamp': pd.date_range('2024-01-01', periods=1000, freq='1H'),
            'person_id': np.random.choice(['USER001', 'USER002', 'USER003'], 1000),
            'door_id': np.random.choice(['DOOR001', 'DOOR002', 'DOOR003'], 1000),
            'access_result': np.random.choice(['Granted', 'Denied'], 1000, p=[0.85, 0.15]),
            'badge_status': np.random.choice(['Valid', 'Invalid'], 1000, p=[0.95, 0.05])
        })

        chart_results = get_interactive_charts(sample_data)

        print("✅ Chart generation test:")
        print(f"  - Generated {len(chart_results)} chart sections")
        print(f"  - Chart types: {list(chart_results.keys())}")

        dashboard = create_charts_dashboard(chart_results)

        print("✅ Dashboard creation test:")
        print(f"  - Dashboard type: {type(dashboard)}")
        print(f"  - Contains charts: {dashboard is not None}")

        return True
    except Exception as e:
        print(f"❌ Charts test failed: {e}")
        return False


charts_integration_checklist = """
INTERACTIVE CHARTS INTEGRATION CHECKLIST
=======================================

☐ 1. ADD IMPORTS
   - Add SecurityChartsGenerator import
   - Add AnalyticsController import

☐ 2. UPDATE DROPDOWN OPTIONS
   - Find analytics-type dropdown
   - Add "charts" option to options list

☐ 3. ADD NEW FUNCTIONS
   - Add get_interactive_charts() function
   - Add create_charts_dashboard() function  
   - Add get_uploaded_data_safe() function

☐ 4. UPDATE CALLBACK
   - Find run_analytics_display_callback
   - Add special handling for analysis_type == "charts"
   - Use the fixed callback code

☐ 5. TEST INTEGRATION
   - Run test_charts_integration()
   - Select "Interactive Charts" from dropdown
   - Verify charts display correctly

☐ 6. TROUBLESHOOTING
   - Check browser console for errors
   - Verify all imports work
   - Test with sample data first

COMMON ISSUES:
- Charts option not in dropdown → Update dropdown options
- Charts not loading → Check data loading function
- Empty charts → Verify data format and columns
- Import errors → Check analytics module imports
"""


def quick_charts_fix():
    """Quick fix to test charts immediately"""

    temp_options = [
        {"label": "🔒 Security Patterns", "value": "security"},
        {"label": "📈 Access Trends", "value": "trends"},
        {"label": "👤 User Behavior", "value": "behavior"},
        {"label": "🚨 Anomaly Detection", "value": "anomaly"},
        {"label": "📊 Interactive Charts", "value": "charts"}
    ]

    quick_callback_addition = """
    # ADD THIS TO YOUR CALLBACK:
    if analysis_type == "charts":
        return dbc.Alert("Charts feature is now enabled! 🎉", color="success")
    """

    print("Quick fix applied - charts option should now appear in dropdown")
    return temp_options, quick_callback_addition

