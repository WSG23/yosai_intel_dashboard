#!/usr/bin/env python3
"""
Streamlined Deep Analytics Page
Works with simplified component system
"""
import logging
from typing import Optional, Dict, Any
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd

# Import simplified components
from components import (
    create_summary_cards, 
    create_analytics_charts, 
    create_data_preview,
    generate_sample_analytics,
    create_loading_spinner,
    create_error_alert,
    create_info_alert
)

logger = logging.getLogger(__name__)


def layout():
    """Deep Analytics page layout - simplified and working"""
    return dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H1("🔍 Deep Analytics", className="text-primary mb-2"),
                html.P(
                    "Advanced data analysis and visualization for security intelligence",
                    className="text-muted mb-4"
                ),
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
                                    options=[
                                        {"label": "Sample Data", "value": "sample"},
                                        {"label": "Uploaded Files", "value": "uploaded"},
                                        {"label": "Database", "value": "database"},
                                    ],
                                    value="sample",
                                    placeholder="Choose data source..."
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
                                        {"label": "Custom Analysis", "value": "custom"},
                                    ],
                                    value="security",
                                    placeholder="Select analysis type..."
                                )
                            ], width=6),
                        ]),
                        html.Hr(),
                        dbc.Button(
                            "🚀 Generate Analytics",
                            id="generate-analytics-btn",
                            color="primary",
                            size="lg",
                            className="mt-2"
                        )
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
        
    ], fluid=True)


# Register callbacks for this page
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
    """Generate and display analytics based on selected parameters"""
    
    if not n_clicks:
        return html.Div(), {}
    
    try:
        # Show loading first
        loading_component = create_loading_spinner("Generating analytics...")
        
        # Get data based on source
        if data_source == "sample":
            analytics_results = generate_sample_analytics()
        elif data_source == "uploaded":
            analytics_results = _get_uploaded_data_analytics()
        elif data_source == "database":
            analytics_results = _get_database_analytics()
        else:
            analytics_results = {}
        
        if not analytics_results:
            return create_info_alert(
                "No data available for the selected source. Try using sample data.",
                "No Data Available"
            ), {}
        
        # Enhance analytics based on type
        enhanced_results = _enhance_analytics_by_type(analytics_results, analysis_type)
        
        # Create display components
        display_components = _create_analytics_display(enhanced_results, analysis_type)
        
        return display_components, enhanced_results
        
    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        return create_error_alert(
            f"Error generating analytics: {str(e)}",
            "Analytics Error"
        ), {}


def _get_uploaded_data_analytics() -> Dict[str, Any]:
    """Get analytics from uploaded data (placeholder)"""
    # This would integrate with file upload system
    logger.info("Getting uploaded data analytics")
    return {}


def _get_database_analytics() -> Dict[str, Any]:
    """Get analytics from database (placeholder)"""
    # This would integrate with database
    logger.info("Getting database analytics")
    return {}


def _enhance_analytics_by_type(base_analytics: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
    """Enhance analytics based on analysis type"""
    enhanced = base_analytics.copy()
    
    if analysis_type == "security":
        enhanced['analysis_focus'] = "Security Patterns"
        enhanced['security_metrics'] = {
            'failed_attempts': 15,
            'after_hours_access': 8,
            'suspicious_patterns': 3
        }
        
    elif analysis_type == "trends":
        enhanced['analysis_focus'] = "Access Trends"
        enhanced['trend_metrics'] = {
            'daily_average': 45,
            'weekly_growth': '12%',
            'peak_hours': '9:00-11:00 AM'
        }
        
    elif analysis_type == "behavior":
        enhanced['analysis_focus'] = "User Behavior"
        enhanced['behavior_metrics'] = {
            'regular_users': 18,
            'irregular_patterns': 2,
            'new_users': 3
        }
        
    elif analysis_type == "custom":
        enhanced['analysis_focus'] = "Custom Analysis"
        enhanced['custom_metrics'] = {
            'custom_score': 85,
            'recommendations': ['Review access policies', 'Update security training']
        }
    
    return enhanced


def _create_analytics_display(analytics_results: Dict[str, Any], analysis_type: str) -> html.Div:
    """Create the complete analytics display"""
    components = []
    
    # Analysis header
    analysis_focus = analytics_results.get('analysis_focus', 'Analytics')
    components.append(
        dbc.Alert([
            html.H5(f"📈 {analysis_focus} Results", className="mb-2"),
            html.P(f"Analysis completed successfully for {analytics_results.get('total_events', 0)} events")
        ], color="success", className="mb-4")
    )
    
    # Summary cards
    if analytics_results:
        components.append(create_summary_cards(analytics_results))
    
    # Charts
    if analytics_results:
        charts_component = create_analytics_charts(analytics_results)
        components.append(
            dbc.Card([
                dbc.CardHeader("📊 Visualizations"),
                dbc.CardBody([charts_component])
            ], className="mb-4")
        )
    
    # Analysis-specific insights
    components.append(_create_insights_section(analytics_results, analysis_type))
    
    return html.Div(components)


def _create_insights_section(analytics_results: Dict[str, Any], analysis_type: str) -> dbc.Card:
    """Create analysis-specific insights section"""
    insights = []
    
    if analysis_type == "security":
        security_metrics = analytics_results.get('security_metrics', {})
        insights = [
            f"🔒 {security_metrics.get('failed_attempts', 0)} failed access attempts detected",
            f"🌙 {security_metrics.get('after_hours_access', 0)} after-hours access events",
            f"⚠️ {security_metrics.get('suspicious_patterns', 0)} suspicious patterns identified"
        ]
        
    elif analysis_type == "trends":
        trend_metrics = analytics_results.get('trend_metrics', {})
        insights = [
            f"📈 Daily average: {trend_metrics.get('daily_average', 0)} events",
            f"📊 Weekly growth: {trend_metrics.get('weekly_growth', 'N/A')}",
            f"⏰ Peak hours: {trend_metrics.get('peak_hours', 'N/A')}"
        ]
        
    elif analysis_type == "behavior":
        behavior_metrics = analytics_results.get('behavior_metrics', {})
        insights = [
            f"👥 {behavior_metrics.get('regular_users', 0)} users with regular patterns",
            f"❓ {behavior_metrics.get('irregular_patterns', 0)} irregular behavior patterns",
            f"🆕 {behavior_metrics.get('new_users', 0)} new users detected"
        ]
        
    elif analysis_type == "custom":
        custom_metrics = analytics_results.get('custom_metrics', {})
        score = custom_metrics.get('custom_score', 0)
        recommendations = custom_metrics.get('recommendations', [])
        insights = [f"📊 Custom Analysis Score: {score}/100"]
        insights.extend([f"💡 {rec}" for rec in recommendations])
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("🔍 Insights & Recommendations", className="mb-0")
        ]),
        dbc.CardBody([
            html.Ul([
                html.Li(insight) for insight in insights
            ]) if insights else html.P("No specific insights available for this analysis type.")
        ])
    ], className="mb-4")


# Export layout function
__all__ = ["layout"]
