"""
Deep Analytics Page - Analytics Only (Upload functionality removed)
Focuses purely on data analysis and visualization
"""
from typing import Optional, Dict, Any, List
import logging

# Define safe_text directly to avoid import issues
def safe_text(text):
    """Return text safely, handling any objects"""
    if text is None:
        return ""
    return str(text)

# Dash components are required for this page
from dash import html, dcc
from dash._callback import callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

# Dash is expected to be installed when this module is used
DASH_AVAILABLE = True

try:
    from components.analytics import (
        create_analytics_charts,
        create_summary_cards,
        create_data_preview,
        AnalyticsGenerator
    )
    ANALYTICS_COMPONENTS_AVAILABLE = True
except ImportError:
    ANALYTICS_COMPONENTS_AVAILABLE = False
    
    # Fallback analytics generator
    class FallbackAnalyticsGenerator:
        @staticmethod
        def generate_analytics(df):
            return {}
    
    AnalyticsGenerator = FallbackAnalyticsGenerator

logger = logging.getLogger(__name__)


def layout():
    """Deep Analytics page layout - Analytics focused"""
    if not DASH_AVAILABLE:
        return "Deep Analytics page not available - Dash components missing"
    
    return dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H1(
                    safe_text("\U0001F50D Deep Analytics"), 
                    className="text-primary mb-0"
                ),
                html.P(
                    safe_text("Advanced data analysis and visualization for security intelligence"),
                    className="text-secondary mb-4",
                ),
            ])
        ]),
        
        # Data source selection
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("\U0001F4CA Data Source Selection", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Select Data Source:"),
                                dcc.Dropdown(
                                    id="analytics-data-source",
                                    options=[
                                        {"label": "Uploaded Files", "value": "uploaded"},
                                        {"label": "Sample Data", "value": "sample"},
                                        {"label": "Database", "value": "database"},
                                    ],
                                    value="sample",  # Default to sample since uploaded might not be available
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
                            "Generate Analytics", 
                            id="generate-analytics-btn",
                            color="primary",
                            className="mt-2"
                        )
                    ])
                ])
            ])
        ]),
        
        # Analytics display area
        html.Div(id="analytics-display-area", className="mt-4"),
        
        # Data stores
        dcc.Store(id="analytics-config-store", data={}),
        dcc.Store(id="analytics-results-store", data={}),
        
    ], fluid=True, className="p-4")


def register_analytics_callbacks(app, container=None):
    """Register deep analytics callbacks"""
    if not DASH_AVAILABLE:
        logger.warning("Analytics callbacks not registered - Dash not available")
        return

    @app.callback(
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
            # Get data based on source
            df = _get_data_from_source(data_source, container)
            
            if df is None or df.empty:
                return _create_no_data_message(data_source), {}
            
            # Generate analytics
            analytics_results = _generate_analytics_by_type(df, analysis_type)
            
            # Create display components
            display_components = _create_analytics_display(analytics_results, analysis_type)
            
            return display_components, analytics_results
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return _create_error_display(str(e)), {}

    @app.callback(
        Output("analytics-data-source", "options"),
        Input("analytics-data-source", "id"),
        prevent_initial_call=False,
    )
    def update_data_source_options(component_id):
        """Update available data sources dynamically"""
        options = [
            {"label": "Sample Data", "value": "sample"},
        ]
        
        # Check for uploaded files (this would connect to file upload page)
        # This is where you'd check the file upload store if needed
        
        # Check for database connection
        if container and _has_database_connection(container):
            options.append({"label": "Database", "value": "database"})
        
        return options


def _get_data_from_source(source: str, container=None):
    """Get data from the specified source"""
    import pandas as pd
    
    if source == "sample":
        return _generate_sample_data()
    elif source == "uploaded":
        # This would interface with the file upload page data
        return _get_uploaded_data()
    elif source == "database":
        return _get_database_data(container)
    else:
        return None


def _generate_sample_data():
    """Generate sample security data for analytics"""
    import pandas as pd
    from datetime import datetime, timedelta
    import random
    
    # Generate sample access data
    data = []
    base_time = datetime.now() - timedelta(days=30)
    
    users = [f"EMP{i:03d}" for i in range(1, 51)]
    doors = ["MAIN_ENTRANCE", "SERVER_ROOM", "LAB_A", "LAB_B", "EXECUTIVE", "STORAGE"]
    results = ["Granted", "Denied"]
    
    for i in range(1000):
        data.append({
            "timestamp": base_time + timedelta(minutes=random.randint(0, 43200)),
            "person_id": random.choice(users),
            "door_id": random.choice(doors),
            "access_result": random.choice(results),
            "badge_id": f"BADGE_{random.randint(1000, 9999)}",
        })
    
    return pd.DataFrame(data)


def _get_uploaded_data():
    """Get data from uploaded files (interface with file upload page)"""
    # This would need to interface with the file upload page's data store
    # For now, return None - implement based on your data sharing strategy
    return None


def _get_database_data(container):
    """Get data from database if available"""
    # Implement database data retrieval if needed
    return None


def _has_database_connection(container):
    """Check if database connection is available"""
    # Implement database connection check
    return False


def _generate_analytics_by_type(df, analysis_type: str):
    """Generate analytics based on the specified type"""
    base_analytics = AnalyticsGenerator.generate_analytics(df)
    
    if analysis_type == "security":
        return _enhance_security_analytics(base_analytics, df)
    elif analysis_type == "trends":
        return _enhance_trend_analytics(base_analytics, df)
    elif analysis_type == "behavior":
        return _enhance_behavior_analytics(base_analytics, df)
    elif analysis_type == "custom":
        return _enhance_custom_analytics(base_analytics, df)
    
    return base_analytics


def _enhance_security_analytics(base_analytics, df):
    """Add security-specific analytics"""
    enhanced = base_analytics.copy()
    
    # Add security-specific metrics
    if not df.empty and 'access_result' in df.columns:
        enhanced['security_metrics'] = {
            'failed_attempts': len(df[df['access_result'] == 'Denied']),
            'success_rate': len(df[df['access_result'] == 'Granted']) / len(df) * 100,
            'suspicious_patterns': _detect_suspicious_patterns(df)
        }
    
    return enhanced


def _enhance_trend_analytics(base_analytics, df):
    """Add trend-specific analytics"""
    enhanced = base_analytics.copy()
    
    # Add trend analysis
    if not df.empty and 'timestamp' in df.columns:
        enhanced['trend_metrics'] = {
            'daily_patterns': _analyze_daily_patterns(df),
            'weekly_trends': _analyze_weekly_trends(df),
            'growth_rate': _calculate_growth_rate(df)
        }
    
    return enhanced


def _enhance_behavior_analytics(base_analytics, df):
    """Add behavior-specific analytics"""
    enhanced = base_analytics.copy()
    
    # Add behavioral analysis
    if not df.empty:
        enhanced['behavior_metrics'] = {
            'user_patterns': _analyze_user_patterns(df),
            'anomaly_detection': _detect_anomalies(df),
            'clustering_results': _perform_user_clustering(df)
        }
    
    return enhanced


def _enhance_custom_analytics(base_analytics, df):
    """Add custom analytics"""
    enhanced = base_analytics.copy()
    enhanced['custom_metrics'] = {
        'custom_analysis': 'Custom analysis would be implemented here'
    }
    return enhanced


def _detect_suspicious_patterns(df):
    """Detect suspicious access patterns"""
    # Implement suspicious pattern detection
    return []


def _analyze_daily_patterns(df):
    """Analyze daily access patterns"""
    # Implement daily pattern analysis
    return {}


def _analyze_weekly_trends(df):
    """Analyze weekly trends"""
    # Implement weekly trend analysis
    return {}


def _calculate_growth_rate(df):
    """Calculate growth rate in access events"""
    # Implement growth rate calculation
    return 0


def _analyze_user_patterns(df):
    """Analyze individual user patterns"""
    # Implement user pattern analysis
    return {}


def _detect_anomalies(df):
    """Detect anomalous behavior"""
    # Implement anomaly detection
    return []


def _perform_user_clustering(df):
    """Perform user clustering analysis"""
    # Implement user clustering
    return {}


def _create_analytics_display(analytics_results, analysis_type):
    """Create the analytics display components"""
    if not ANALYTICS_COMPONENTS_AVAILABLE:
        return html.Div("Analytics components not available")
    
    components = []
    
    # Summary cards
    if analytics_results:
        components.append(
            dbc.Row([
                dbc.Col([
                    create_summary_cards(analytics_results)
                ])
            ], className="mb-4")
        )
        
        # Charts
        components.append(
            dbc.Row([
                dbc.Col([
                    create_analytics_charts(analytics_results)
                ])
            ], className="mb-4")
        )
        
        # Analysis-specific components
        if analysis_type == "security":
            components.append(_create_security_analysis_section(analytics_results))
        elif analysis_type == "trends":
            components.append(_create_trend_analysis_section(analytics_results))
        elif analysis_type == "behavior":
            components.append(_create_behavior_analysis_section(analytics_results))
    
    return html.Div(components)


def _create_security_analysis_section(analytics_results):
    """Create security-specific analysis section"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("\U0001F512 Security Analysis", className="mb-0")
        ]),
        dbc.CardBody([
            html.P("Security-specific analysis would be displayed here"),
            # Add security-specific visualizations
        ])
    ], className="mb-4")


def _create_trend_analysis_section(analytics_results):
    """Create trend-specific analysis section"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("\U0001F4C8 Trend Analysis", className="mb-0")
        ]),
        dbc.CardBody([
            html.P("Trend analysis would be displayed here"),
            # Add trend-specific visualizations
        ])
    ], className="mb-4")


def _create_behavior_analysis_section(analytics_results):
    """Create behavior-specific analysis section"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("\U0001F464 Behavior Analysis", className="mb-0")
        ]),
        dbc.CardBody([
            html.P("Behavioral analysis would be displayed here"),
            # Add behavior-specific visualizations
        ])
    ], className="mb-4")


def _create_no_data_message(data_source):
    """Create no data available message"""
    return dbc.Alert([
        html.I(className="fas fa-info-circle me-2"),
        f"No data available from source: {safe_text(data_source)}",
        html.Hr(),
        html.P("Please upload files using the File Upload page or select a different data source.", className="mb-0")
    ], color="info")


def _create_error_display(error_message):
    """Create error display"""
    return dbc.Alert([
        html.I(className="fas fa-exclamation-triangle me-2"),
        f"Error generating analytics: {safe_text(error_message)}"
    ], color="danger")


__all__ = ["layout", "register_analytics_callbacks"]
