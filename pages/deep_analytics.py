#!/usr/bin/env python3
"""
Complete Analytics Integration - Fixed analytics page with full service integration
"""
import logging
from typing import Optional, Dict, Any, List, Union
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import json

# Import complete integration components
from components import (
    create_summary_cards,
    create_analytics_charts,
    create_loading_spinner,
    create_error_alert,
    create_info_alert,
    create_success_alert
)
from services.analytics_service import get_analytics_service

logger = logging.getLogger(__name__)


def sanitize_for_json_store(data: Any) -> Any:
    """Sanitize data for JSON serialization in dcc.Store components."""
    if data is None:
        return None

    if isinstance(data, (str, int, float, bool)):
        return data

    if isinstance(data, datetime):
        return data.isoformat()

    if isinstance(data, pd.Timestamp):
        return data.isoformat()

    if isinstance(data, pd.DataFrame):
        return {
            "type": "dataframe",
            "shape": data.shape,
            "columns": list(data.columns),
            "data": data.head(100).to_dict("records"),
            "dtypes": {col: str(dtype) for col, dtype in data.dtypes.items()},
            "total_rows": len(data),
        }

    if isinstance(data, (pd.Series, list)):
        return [sanitize_for_json_store(item) for item in data]

    if isinstance(data, dict):
        return {key: sanitize_for_json_store(value) for key, value in data.items()}

    if isinstance(data, tuple):
        return [sanitize_for_json_store(item) for item in data]

    if hasattr(data, "__dict__"):
        return {
            "type": type(data).__name__,
            "data": sanitize_for_json_store(data.__dict__),
        }

    return str(data)


def layout():
    """Complete analytics page layout with full integration"""
    # Get analytics service to check available data sources
    analytics_service = get_analytics_service()
    data_source_options = analytics_service.get_data_source_options()

    return dbc.Container([
        # Page header with service health
        dbc.Row([
            dbc.Col([
                html.H1("🔍 Deep Analytics", className="text-primary mb-2"),
                html.P(
                    "Advanced data analysis with integrated data sources",
                    className="text-muted mb-3"
                ),
                # Service health indicator
                html.Div(id="service-health-indicator")
            ])
        ]),

        # Analytics configuration
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📊 Analytics Configuration", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Data Source:"),
                                dcc.Dropdown(
                                    id="analytics-data-source",
                                    options=data_source_options,
                                    value="sample",
                                    placeholder="Choose data source..."
                                ),
                                html.Small(
                                    id="data-source-info",
                                    className="text-muted mt-1"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Analysis Type:"),
                                dcc.Dropdown(
                                    id="analytics-type",
                                    options=[
                                        {"label": "Security Patterns", "value": "security"},
                                        {"label": "Access Trends", "value": "trends"},
                                        {"label": "User Behavior", "value": "behavior"},
                                        {"label": "Anomaly Detection", "value": "anomaly"},
                                    ],
                                    value="security",
                                    placeholder="Select analysis type..."
                                )
                            ], width=6),
                        ]),
                        html.Hr(),
                        dbc.ButtonGroup([
                            dbc.Button(
                                "🚀 Generate Analytics",
                                id="generate-analytics-btn",
                                color="primary",
                                size="lg"
                            ),
                            dbc.Button(
                                "🔄 Refresh Data Sources",
                                id="refresh-sources-btn",
                                color="outline-secondary",
                                size="lg"
                            )
                        ])
                    ])
                ])
            ])
        ], className="mb-4"),

        # Analytics display area
        dbc.Row([
            dbc.Col([
                html.Div(id="analytics-display-area")
            ])
        ]),

        # Data stores
        dcc.Store(id="analytics-results-store", data={}),
        dcc.Store(id="service-health-store", data={}),

        # Hidden div to trigger initial service health check
        html.Div(id="init-trigger", style={"display": "none"})

    ], fluid=True)


@callback(
    [
        Output("service-health-indicator", "children"),
        Output("service-health-store", "data")
    ],
    [
        Input("init-trigger", "children"),
        Input("refresh-sources-btn", "n_clicks")
    ],
    prevent_initial_call=False
)
def update_service_health(init_trigger, refresh_clicks):
    """Update service health indicator"""
    try:
        analytics_service = get_analytics_service()
        health = analytics_service.health_check()

        # Create health indicator
        indicators = []

        # Service status
        service_color = "success" if health.get('service') == 'healthy' else "warning"
        indicators.append(
            dbc.Badge(f"Service: {health.get('service', 'unknown')}", color=service_color, className="me-2")
        )

        # Database status
        db_status = health.get('database', 'unknown')
        db_color = "success" if db_status == 'healthy' else "warning" if db_status == 'not_configured' else "danger"
        indicators.append(
            dbc.Badge(f"Database: {db_status}", color=db_color, className="me-2")
        )

        # Uploaded files
        uploaded_files = health.get('uploaded_files', 0)
        if isinstance(uploaded_files, int):
            file_color = "success" if uploaded_files > 0 else "secondary"
            indicators.append(
                dbc.Badge(f"Uploaded Files: {uploaded_files}", color=file_color, className="me-2")
            )

        health_indicator = html.Div([
            html.Small("Service Health: ", className="text-muted me-2"),
            *indicators
        ], className="mb-3")

        return health_indicator, health

    except Exception as e:
        logger.error(f"Error checking service health: {e}")
        return create_error_alert(f"Health check failed: {str(e)}", "Service Health"), {}


@callback(
    Output("data-source-info", "children"),
    Input("analytics-data-source", "value"),
    State("service-health-store", "data")
)
def update_data_source_info(selected_source, health_data):
    """Update data source information"""
    if not selected_source:
        return ""

    info_text = ""
    if selected_source == "sample":
        info_text = "Using generated sample data for demonstration"
    elif selected_source == "uploaded":
        uploaded_count = health_data.get('uploaded_files', 0) if health_data else 0
        info_text = f"Using {uploaded_count} uploaded file(s)"
    elif selected_source == "database":
        db_status = health_data.get('database', 'unknown') if health_data else 'unknown'
        info_text = f"Using database (status: {db_status})"

    return info_text


@callback(
    [
        Output("analytics-display-area", "children"),
        Output("analytics-results-store", "data"),
    ],
    [
        Input("generate-analytics-btn", "n_clicks"),
    ],
    [
        State("analytics-data-source", "value"),
        State("analytics-type", "value"),
    ],
    prevent_initial_call=True,
)
def generate_analytics_display(
    n_clicks: Optional[int],
    data_source: str,
    analysis_type: str,
):
    """Generate and display complete analytics with service integration - SIMPLIFIED VERSION"""

    if not n_clicks:
        return html.Div(), {}

    loading_component = create_loading_spinner(
        "Generating analytics from integrated services..."
    )

    try:
        analytics_service = get_analytics_service()
        analytics_results = analytics_service.get_analytics_by_source(data_source)

        logger.info(
            f"Analytics results: {analytics_results.get('total_events', 0)} events from {data_source}"
        )
        if analytics_results.get('source_info'):
            logger.info(f"Source info: {analytics_results['source_info']}")

        if not analytics_results or analytics_results.get('total_events', 0) == 0:
            error_info = analytics_results.get('error', 'Unknown error') if analytics_results else 'No results'
            return create_error_alert(
                f"File processing issue: {error_info}. "
                "Check column names match expected format (person_id, door_id, access_result, timestamp).",
                "Data Processing Error"
            ), {}

        enhanced_results = _enhance_analytics_by_type(
            analytics_results, analysis_type
        )
        display_components = _create_complete_analytics_display(
            enhanced_results, analysis_type, data_source
        )

        logger.info(
            f"Generated analytics for {data_source} source with {enhanced_results.get('total_events', 0)} events"
        )

        # Return display components and results (now JSON-safe from source)
        return display_components, enhanced_results

    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        error_data = {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat(),
        }
        return (
            create_error_alert(
                f"Analytics generation failed: {str(e)}", "Analytics Error"
            ),
            error_data,
        )


def _enhance_analytics_by_type(base_analytics: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
    """Enhance analytics based on analysis type with complete integration - FIXED VERSION"""
    enhanced = base_analytics.copy()

    # Add analysis type metadata
    enhanced['analysis_type'] = analysis_type
    # CRITICAL FIX: Use datetime.now() instead of pd.Timestamp.now()
    enhanced['generated_at'] = datetime.now().isoformat()

    if analysis_type == "security":
        enhanced['analysis_focus'] = "Security Patterns"
        enhanced['security_metrics'] = {
            'failed_attempts': len([p for p, c in enhanced.get('access_patterns', {}).items() \
                                  if 'fail' in p.lower() or 'denied' in p.lower()]),
            'suspicious_patterns': enhanced.get('anomalies', {}).get('total_anomalies', 0),
            'security_score': _calculate_security_score(enhanced)
        }

    elif analysis_type == "trends":
        enhanced['analysis_focus'] = "Access Trends"
        total_events = enhanced.get('total_events', 0)
        date_range = enhanced.get('date_range', {})
        days_range = _calculate_days_in_range(date_range)

        enhanced['trend_metrics'] = {
            'daily_average': round(total_events / max(days_range, 1), 1),
            'events_per_user': round(total_events / max(len(enhanced.get('top_users', [])), 1), 1),
            'peak_activity': _identify_peak_activity(enhanced)
        }

    elif analysis_type == "behavior":
        enhanced['analysis_focus'] = "User Behavior Analysis"
        enhanced['behavior_metrics'] = {
            'active_users': len(enhanced.get('top_users', [])),
            'average_access_per_user': _calculate_avg_access_per_user(enhanced),
            'behavioral_anomalies': enhanced.get('anomalies', {}).get('total_anomalies', 0)
        }

    elif analysis_type == "anomaly":
        enhanced['analysis_focus'] = "Anomaly Detection"
        anomalies = enhanced.get('anomalies', {})
        enhanced['anomaly_metrics'] = {
            'total_anomalies': anomalies.get('total_anomalies', 0),
            'anomaly_rate': _calculate_anomaly_rate(enhanced),
            'critical_anomalies': anomalies.get('anomaly_types', {}).get('failed_access', 0)
        }

    return enhanced


def _create_complete_analytics_display(analytics_results: Dict[str, Any], analysis_type: str, data_source: str) -> html.Div:
    """Create complete analytics display with all integrated components"""
    components = []

    # Success header with metadata
    analysis_focus = analytics_results.get('analysis_focus', 'Analytics')
    total_events = analytics_results.get('total_events', 0)

    components.append(
        create_success_alert(
            f"Analysis completed successfully! Processed {total_events:,} events from {data_source} source.",
            f"📈 {analysis_focus} Results"
        )
    )

    # Summary cards
    if analytics_results:
        components.append(create_summary_cards(analytics_results))

    # Charts
    if analytics_results:
        charts_component = create_analytics_charts(analytics_results)
        components.append(
            dbc.Card([
                dbc.CardHeader([
                    html.H5("📊 Data Visualizations", className="mb-0")
                ]),
                dbc.CardBody([charts_component])
            ], className="mb-4")
        )

    # Analysis-specific insights
    components.append(_create_enhanced_insights_section(analytics_results, analysis_type))

    # Data source information
    components.append(_create_data_source_info_section(analytics_results, data_source))

    return html.Div(components)


def _create_enhanced_insights_section(analytics_results: Dict[str, Any], analysis_type: str) -> dbc.Card:
    """Create enhanced insights section with complete integration"""
    insights = []
    recommendations = []

    if analysis_type == "security":
        security_metrics = analytics_results.get('security_metrics', {})
        insights = [
            f"🔒 Security Score: {security_metrics.get('security_score', 'N/A')}/100",
            f"⚠️ Failed Attempts: {security_metrics.get('failed_attempts', 0)}",
            f"🚨 Suspicious Patterns: {security_metrics.get('suspicious_patterns', 0)}",
        ]
        recommendations = [
            "Review failed access attempts for potential security threats",
            "Implement additional monitoring for after-hours access",
            "Consider multi-factor authentication for sensitive areas"
        ]

    elif analysis_type == "trends":
        trend_metrics = analytics_results.get('trend_metrics', {})
        insights = [
            f"📈 Daily Average: {trend_metrics.get('daily_average', 0)} events",
            f"👤 Events per User: {trend_metrics.get('events_per_user', 0)}",
            f"⏰ Peak Activity: {trend_metrics.get('peak_activity', 'Unknown')}",
        ]
        recommendations = [
            "Monitor peak usage times for resource planning",
            "Analyze access patterns for operational efficiency",
            "Plan maintenance during low-activity periods"
        ]

    elif analysis_type == "behavior":
        behavior_metrics = analytics_results.get('behavior_metrics', {})
        insights = [
            f"👥 Active Users: {behavior_metrics.get('active_users', 0)}",
            f"📊 Avg Access/User: {behavior_metrics.get('average_access_per_user', 0)}",
            f"❓ Behavioral Anomalies: {behavior_metrics.get('behavioral_anomalies', 0)}",
        ]
        recommendations = [
            "Investigate users with unusual access patterns",
            "Provide access control training for frequent users",
            "Review access permissions for inactive users"
        ]

    elif analysis_type == "anomaly":
        anomaly_metrics = analytics_results.get('anomaly_metrics', {})
        insights = [
            f"🚨 Total Anomalies: {anomaly_metrics.get('total_anomalies', 0)}",
            f"📊 Anomaly Rate: {anomaly_metrics.get('anomaly_rate', 0):.2f}%",
            f"🔴 Critical Anomalies: {anomaly_metrics.get('critical_anomalies', 0)}",
        ]
        recommendations = [
            "Investigate all critical anomalies immediately",
            "Set up automated alerts for anomaly detection",
            "Review access policies to reduce false positives"
        ]

    return dbc.Card([
        dbc.CardHeader([
            html.H5("🔍 Insights & Recommendations", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6("📊 Key Insights:", className="text-primary"),
                    html.Ul([html.Li(insight) for insight in insights]) if insights \
                    else html.P("No specific insights available.", className="text-muted")
                ], width=6),
                dbc.Col([
                    html.H6("💡 Recommendations:", className="text-success"),
                    html.Ul([html.Li(rec) for rec in recommendations]) if recommendations
                    else html.P("No recommendations generated.", className="text-muted")
                ], width=6)
            ])
        ])
    ], className="mb-4")


def _create_data_source_info_section(analytics_results: Dict[str, Any], data_source: str) -> dbc.Card:
    """Create data source information section"""
    source_info = analytics_results.get('data_source', data_source)
    date_range = analytics_results.get('date_range', {})

    return dbc.Card([
        dbc.CardHeader([
            html.H6("📋 Data Source Information", className="mb-0")
        ]),
        dbc.CardBody([
            html.Dl([
                html.Dt("Source Type:"),
                html.Dd(source_info),
                html.Dt("Date Range:"),
                html.Dd(f"{date_range.get('start', 'Unknown')} to {date_range.get('end', 'Unknown')}"),
                html.Dt("Total Records:"),
                html.Dd(f"{analytics_results.get('total_events', 0):,}"),
                html.Dt("Generated At:"),
                html.Dd(analytics_results.get('generated_at', 'Unknown'))
            ])
        ])
    ], className="mb-4")


# Helper functions for calculations

def _calculate_security_score(analytics: Dict[str, Any]) -> int:
    """Calculate security score based on analytics"""
    total_events = analytics.get('total_events', 1)
    access_patterns = analytics.get('access_patterns', {})

    failed_events = sum(count for pattern, count in access_patterns.items() \
                       if 'fail' in pattern.lower() or 'denied' in pattern.lower())

    success_rate = ((total_events - failed_events) / total_events) * 100
    return max(0, min(100, int(success_rate)))


def _calculate_days_in_range(date_range: Dict[str, str]) -> int:
    """Calculate number of days in date range"""
    try:
        import pandas as pd
        start = pd.to_datetime(date_range.get('start'))
        end = pd.to_datetime(date_range.get('end'))
        return (end - start).days + 1
    except:
        return 7  # Default to 7 days


def _identify_peak_activity(analytics: Dict[str, Any]) -> str:
    """Identify peak activity period"""
    # Simple implementation - could be enhanced with actual time analysis
    return "9:00 AM - 5:00 PM (Business Hours)"


def _calculate_avg_access_per_user(analytics: Dict[str, Any]) -> float:
    """Calculate average access per user"""
    total_events = analytics.get('total_events', 0)
    users = analytics.get('top_users', [])
    return round(total_events / max(len(users), 1), 1)


def _calculate_anomaly_rate(analytics: Dict[str, Any]) -> float:
    """Calculate anomaly rate as percentage"""
    total_events = analytics.get('total_events', 1)
    total_anomalies = analytics.get('anomalies', {}).get('total_anomalies', 0)
    return (total_anomalies / total_events) * 100


# Export layout function
__all__ = ["layout"]
