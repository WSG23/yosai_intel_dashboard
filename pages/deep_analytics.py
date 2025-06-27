#!/usr/bin/env python3
"""
CLEANED Deep Analytics - Duplicate callbacks removed
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

# Dash core imports
from dash import html, dcc, callback, Input, Output, State, ALL, MATCH, ctx
from dash import callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

# Services with safe imports
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

logger = logging.getLogger(__name__)


# =============================================================================
# SAFE SERVICE UTILITIES
# =============================================================================

def get_analytics_service_safe():
    """Safely get analytics service"""
    try:
        from services.analytics_service import AnalyticsService
        return AnalyticsService()
    except ImportError:
        return None
    except Exception:
        return None


def get_data_source_options_safe():
    """Get available data sources safely"""
    options = [{"label": "None selected", "value": "none"}]
    
    try:
        from pages.file_upload import get_uploaded_filenames
        filenames = get_uploaded_filenames()
        
        for filename in filenames:
            options.append({
                "label": f"📄 {filename}",
                "value": f"upload:{filename}"
            })
    except ImportError:
        pass
    
    # Add service data sources
    try:
        service = get_analytics_service_safe()
        if service:
            service_sources = service.get_available_sources()
            for source in service_sources:
                options.append({
                    "label": f"🔧 {source}",
                    "value": f"service:{source}"
                })
    except Exception:
        pass
    
    return options


def get_initial_message_safe():
    """Safe initial message"""
    return dbc.Alert([
        html.H6("Get Started"),
        html.P("1. Select a data source from the dropdown"),
        html.P("2. Click any analysis button to run immediately"),
        html.P("Each button runs its analysis type automatically")
    ], color="info")


def process_suggests_analysis_safe(data_source: str) -> Dict[str, Any]:
    """Safe suggests analysis"""
    try:
        if data_source.startswith("upload:") or data_source == "service:uploaded":
            from pages.file_upload import get_uploaded_data
            uploaded_files = get_uploaded_data()
            if not uploaded_files:
                return {"error": "No uploaded files found"}
            
            filename = data_source.replace("upload:", "") if data_source.startswith("upload:") else list(uploaded_files.keys())[0]
            df = uploaded_files.get(filename)
            if df is None:
                return {"error": f"File {filename} not found"}
            
            suggestions = get_ai_suggestions_for_file(df, filename)
            return {
                "analysis_type": "AI Suggestions",
                "filename": filename,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "suggestions": suggestions
            }
        return {"error": "Suggests analysis only available for uploaded files"}
    except Exception as e:
        return {"error": f"Suggests analysis error: {str(e)}"}


def process_quality_analysis_safe(data_source: str) -> Dict[str, Any]:
    """Safe data quality analysis"""
    try:
        if data_source.startswith("upload:") or data_source == "service:uploaded":
            from pages.file_upload import get_uploaded_data
            uploaded_files = get_uploaded_data()
            if not uploaded_files:
                return {"error": "No uploaded files found"}
            filename = data_source.replace("upload:", "") if data_source.startswith("upload:") else list(uploaded_files.keys())[0]
            df = uploaded_files.get(filename)
            if df is None:
                return {"error": f"File {filename} not found"}
            total_rows = len(df)
            total_cols = len(df.columns)
            missing_values = df.isnull().sum().sum()
            duplicate_rows = df.duplicated().sum()
            quality_score = max(0, 100 - (missing_values + duplicate_rows) / total_rows * 100)
            return {
                "analysis_type": "Data Quality",
                "filename": filename,
                "total_rows": total_rows,
                "total_columns": total_cols,
                "missing_values": int(missing_values),
                "duplicate_rows": int(duplicate_rows),
                "quality_score": round(quality_score, 1)
            }
        return {"error": "Data quality analysis only available for uploaded files"}
    except Exception as e:
        return {"error": f"Quality analysis error: {str(e)}"}


def analyze_data_with_service_safe(data_source, analysis_type):
    """Safe service-based analysis"""
    try:
        service = get_analytics_service_safe()
        if not service:
            return {"error": "Analytics service not available"}
        source_name = data_source.replace("service:", "") if data_source.startswith("service:") else "uploaded"
        analytics_results = service.get_analytics_by_source(source_name)
        if analytics_results.get('status') == 'error':
            return {"error": analytics_results.get('message', 'Unknown error')}
        return {
            "analysis_type": analysis_type.title(),
            "data_source": data_source,
            "total_events": analytics_results.get('total_events', 0),
            "unique_users": analytics_results.get('unique_users', 0),
            "success_rate": analytics_results.get('success_rate', 0),
            "status": "completed"
        }
    except Exception as e:
        return {"error": f"Service analysis failed: {str(e)}"}


def create_analysis_results_display_safe(results, analysis_type):
    """Create safe results display without Unicode issues"""
    try:
        if isinstance(results, dict) and "error" in results:
            return dbc.Alert(str(results["error"]), color="danger")
        content = [
            html.H5(f"{analysis_type.title()} Results"),
            html.Hr()
        ]
        if analysis_type == "suggests" and "suggestions" in results:
            content.extend([
                html.P(f"File: {results.get('filename', 'Unknown')}"),
                html.P(f"Columns analyzed: {results.get('total_columns', 0)}"),
                html.P(f"Rows processed: {results.get('total_rows', 0)}"),
                html.H6("AI Column Suggestions:"),
                html.Div([
                    html.P(f"{col}: {info.get('field', 'unknown')} (confidence: {info.get('confidence', 0):.1f})")
                    for col, info in results.get('suggestions', {}).items()
                ])
            ])
        elif analysis_type == "quality":
            content.extend([
                html.P(f"Total rows: {results.get('total_rows', 0):,}"),
                html.P(f"Total columns: {results.get('total_columns', 0)}"),
                html.P(f"Missing values: {results.get('missing_values', 0):,}"),
                html.P(f"Duplicate rows: {results.get('duplicate_rows', 0):,}"),
                html.P(f"Quality score: {results.get('quality_score', 0):.1f}%")
            ])
        else:
            content.extend([
                html.P(f"Total events: {results.get('total_events', 0):,}"),
                html.P(f"Unique users: {results.get('unique_users', 0):,}"),
                html.P(f"Success rate: {results.get('success_rate', 0):.1%}")
            ])
        return dbc.Card([
            dbc.CardBody(content)
        ])
    except Exception as e:
        return dbc.Alert(f"Display error: {str(e)}", color="danger")


# =============================================================================
# LAYOUT FUNCTION
# =============================================================================

def layout():
    """Main analytics page layout"""
    try:
        # Header section
        header = dbc.Row([
            dbc.Col([
                html.H2("Deep Analytics"),
                html.P("Advanced data analysis and insights"),
                html.Hr()
            ])
        ])

        # Configuration card
        config_card = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Data Source", className="fw-bold mb-2"),
                        dcc.Dropdown(
                            id="analytics-data-source",
                            options=get_data_source_options_safe(),
                            value="none",
                            placeholder="Select data source..."
                        )
                    ], md=6),
                    dbc.Col([
                        html.Label("Analysis Type", className="fw-bold mb-3"),
                        dbc.Row([
                            dbc.Col(dbc.Button("Security", id="security-btn", color="danger", outline=True, size="sm", className="w-100 mb-2"), width=6),
                            dbc.Col(dbc.Button("Trends", id="trends-btn", color="info", outline=True, size="sm", className="w-100 mb-2"), width=6),
                            dbc.Col(dbc.Button("Behavior", id="behavior-btn", color="warning", outline=True, size="sm", className="w-100 mb-2"), width=6),
                            dbc.Col(dbc.Button("Anomaly", id="anomaly-btn", color="dark", outline=True, size="sm", className="w-100 mb-2"), width=6),
                            dbc.Col(dbc.Button("AI Suggestions", id="suggests-btn", color="success", outline=True, size="sm", className="w-100 mb-2"), width=6),
                            dbc.Col(dbc.Button("Quality", id="quality-btn", color="secondary", outline=True, size="sm", className="w-100 mb-2"), width=6),
                        ])
                    ], md=6)
                ])
            ])
        ], className="mb-4")

        # Simple unique patterns card  
        simple_unique_patterns_card = dbc.Card([
            dbc.CardBody([
                html.H5("Quick Pattern Analysis"),
                dbc.Button("Unique Patterns", id="unique-patterns-btn", color="primary", className="mb-3"),
                html.Div(id="unique-patterns-output")
            ])
        ], className="mb-4")

        # Results area
        results_area = dbc.Row([
            dbc.Col([
                html.Div(id="analytics-display-area", children=[
                    get_initial_message_safe()
                ])
            ])
        ])

        # Hidden stores
        stores = [
            dcc.Store(id="analytics-results-store", data={}),
            dcc.Store(id="service-health-store", data={}),
            html.Div(id="hidden-trigger", style={"display": "none"})
        ]

        return dbc.Container([header, config_card, simple_unique_patterns_card, results_area] + stores, fluid=True)

    except Exception as e:
        logger.error(f"Layout creation error: {e}")
        return dbc.Container([
            dbc.Alert([
                html.H4("Page Loading Error"),
                html.P(f"Error: {str(e)}"),
                html.P("Please check imports and dependencies")
            ], color="danger")
        ], fluid=True)


# =============================================================================
# SINGLE CALLBACK - No duplicates
# =============================================================================

@callback(
    Output("analytics-display-area", "children"),
    [
        Input("security-btn", "n_clicks"),
        Input("trends-btn", "n_clicks"),
        Input("behavior-btn", "n_clicks"), 
        Input("anomaly-btn", "n_clicks"),
        Input("suggests-btn", "n_clicks"),
        Input("quality-btn", "n_clicks"),
        Input("unique-patterns-btn", "n_clicks")
    ],
    [State("analytics-data-source", "value")],
    prevent_initial_call=True
)
def handle_analysis_buttons(security_n, trends_n, behavior_n, anomaly_n, suggests_n, quality_n, unique_n, data_source):
    """Handle analysis button clicks with safe text encoding"""
    
    if not callback_context.triggered:
        return get_initial_message_safe()
    
    # Check data source first
    if not data_source or data_source == "none":
        return dbc.Alert("Please select a data source first", color="warning")
    
    # Get which button was clicked
    button_id = callback_context.triggered[0]['prop_id'].split('.')[0]
    
    # Map button to analysis type
    analysis_map = {
        "security-btn": "security",
        "trends-btn": "trends", 
        "behavior-btn": "behavior",
        "anomaly-btn": "anomaly",
        "suggests-btn": "suggests",
        "quality-btn": "quality",
        "unique-patterns-btn": "unique_patterns"
    }
    
    analysis_type = analysis_map.get(button_id)
    if not analysis_type:
        return dbc.Alert("Unknown analysis type", color="danger")
    
    # Route to appropriate analysis function
    if analysis_type == "suggests":
        results = process_suggests_analysis_safe(data_source)
    elif analysis_type == "quality":
        results = process_quality_analysis_safe(data_source)
    elif analysis_type == "unique_patterns":
        # Handle unique patterns analysis
        try:
            analytics_service = AnalyticsService()
            results = analytics_service.get_unique_patterns_analysis()
            if results['status'] == 'success':
                data_summary = results['data_summary']
                user_patterns = results['user_patterns']
                device_patterns = results['device_patterns']
                return html.Div([
                    html.H4("Analysis Results"),
                    html.P(f"Total Records: {data_summary['total_records']:,}"),
                    html.P(f"Unique Users: {data_summary['unique_entities']['users']:,}"),
                    html.P(f"Unique Devices: {data_summary['unique_entities']['devices']:,}"),
                    html.P(f"Power Users: {len(user_patterns['user_classifications']['power_users']):,}"),
                    html.P(f"High Traffic Devices: {len(device_patterns['device_classifications']['high_traffic_devices']):,}"),
                    html.P(f"Success Rate: {results['access_patterns']['overall_success_rate']:.1%}")
                ])
            else:
                return dbc.Alert(f"Error: {results.get('message', 'Analysis failed')}", color="danger")
        except Exception as e:
            return dbc.Alert(f"Error: {str(e)}", color="danger")
    else:
        results = analyze_data_with_service_safe(data_source, analysis_type)
    
    # Handle errors
    if isinstance(results, dict) and "error" in results:
        return dbc.Alert(str(results["error"]), color="danger")
    
    # Create display
    return create_analysis_results_display_safe(results, analysis_type)


# Export for testing
__all__ = ["layout", "handle_analysis_buttons"]
