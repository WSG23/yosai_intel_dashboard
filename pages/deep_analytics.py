#!/usr/bin/env python3
"""
Deep Analytics UI Fix - Modular Replacement Code
Fixes suggests not showing and UI display issues
"""

# =============================================================================
# SECTION 1: CONSOLIDATED IMPORTS
# Replace the import section at the top of pages/deep_analytics.py
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

# Internal service imports with safe fallbacks
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
    """Safely get available data sources with suggests integration"""
    options = []

    try:
        # CORRECTED IMPORT - Use get_uploaded_data instead of get_uploaded_data_store
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
                    has_suggestions = bool(suggestions and any(
                        s.get('field') for s in suggestions.values()
                    ))
                    print(f"      🤖 AI suggestions: {'Available' if has_suggestions else 'None'}")
                except Exception as e:
                    print(f"      ⚠️ AI suggestions failed: {e}")
                    pass

            suggestion_indicator = " 🤖" if has_suggestions else " 📄"
            options.append({
                "label": f"{filename}{suggestion_indicator}",
                "value": f"upload:{filename}"
            })
    except ImportError as e:
        print(f"❌ Import error: {e}")
        options.append({
            "label": "⚠️ File upload module not available",
            "value": "none"
        })
    except Exception as e:
        print(f"❌ Error getting uploaded files: {e}")
        options.append({
            "label": f"⚠️ Error: {str(e)}",
            "value": "none"
        })

    # Add service-based sources if available
    try:
        service = get_analytics_service_safe()
        if service:
            service_sources = service.get_available_sources()
            for source in service_sources:
                options.append({
                    "label": f"🔗 {source}",
                    "value": f"service:{source}"
                })
    except Exception as e:
        print(f"⚠️ Service sources unavailable: {e}")

    if not options:
        options.append({
            "label": "No data sources available - Upload files first",
            "value": "none"
        })

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
        {"label": "📊 Data Quality", "value": "quality"}
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

        if data_source.startswith("upload:"):
            filename = data_source.replace("upload:", "")
            print(f"📄 Looking for uploaded file: {filename}")

            # CORRECTED IMPORT - Use get_uploaded_data
            from pages.file_upload import get_uploaded_data
            uploaded_files = get_uploaded_data()

            print(f"🔍 Available files: {list(uploaded_files.keys())}")

            if filename not in uploaded_files:
                return {"error": f"File {filename} not found in uploaded files"}

            df = uploaded_files[filename]
            print(f"✅ Found file with {len(df):,} rows × {len(df.columns)} columns")

            # Get AI suggestions
            if AI_SUGGESTIONS_AVAILABLE:
                try:
                    suggestions = get_ai_suggestions_for_file(df, filename)
                    print(f"🤖 Generated {len(suggestions)} AI suggestions")

                    # Process suggestions for display
                    processed_suggestions = []
                    total_confidence = 0
                    confident_mappings = 0

                    for column, suggestion in suggestions.items():
                        field = suggestion.get('field', '')
                        confidence = suggestion.get('confidence', 0.0)

                        status = "🟢 High" if confidence >= 0.7 else "🟡 Medium" if confidence >= 0.4 else "🔴 Low"

                        # Get sample data safely
                        try:
                            sample_data = df[column].dropna().head(3).astype(str).tolist()
                        except Exception:
                            sample_data = ["N/A"]

                        processed_suggestions.append({
                            "column": column,
                            "suggested_field": field if field else "No suggestion",
                            "confidence": confidence,
                            "status": status,
                            "sample_data": sample_data
                        })

                        total_confidence += confidence
                        if confidence >= 0.6:
                            confident_mappings += 1

                    avg_confidence = total_confidence / len(suggestions) if suggestions else 0

                    # Get data preview safely
                    try:
                        data_preview = df.head(5).to_dict('records')
                    except Exception:
                        data_preview = []

                    result = {
                        "filename": filename,
                        "total_columns": len(df.columns),
                        "total_rows": len(df),
                        "suggestions": processed_suggestions,
                        "avg_confidence": avg_confidence,
                        "confident_mappings": confident_mappings,
                        "data_preview": data_preview,
                        "column_names": list(df.columns)
                    }

                    print(f"✅ Processed suggests analysis: {avg_confidence:.1%} avg confidence")
                    return result

                except Exception as e:
                    print(f"❌ AI suggestions processing failed: {e}")
                    return {"error": f"AI suggestions failed: {str(e)}"}
            else:
                return {"error": "AI suggestions service not available"}
        else:
            return {"error": "Suggests analysis only available for uploaded files"}

    except Exception as e:
        print(f"❌ Error processing suggests analysis: {e}")
        return {"error": f"Failed to process suggests: {str(e)}"}

# =============================================================================
# SECTION 4: SUGGESTS DISPLAY COMPONENTS
# Add these functions to create suggests UI components
# =============================================================================

def create_suggests_display(suggests_data: Dict[str, Any]) -> html.Div:
    """Create suggests analysis display components"""
    if "error" in suggests_data:
        return dbc.Alert(f"Error: {suggests_data['error']}", color="danger")
    
    try:
        filename = suggests_data.get("filename", "Unknown")
        suggestions = suggests_data.get("suggestions", [])
        avg_confidence = suggests_data.get("avg_confidence", 0)
        confident_mappings = suggests_data.get("confident_mappings", 0)
        total_columns = suggests_data.get("total_columns", 0)
        
        # Summary card
        summary_card = dbc.Card([
            dbc.CardHeader([
                html.H5(f"🤖 AI Column Mapping Analysis - {filename}")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H6("Overall Confidence"),
                        dbc.Progress(
                            value=avg_confidence * 100,
                            label=f"{avg_confidence:.1%}",
                            color="success" if avg_confidence >= 0.7 else "warning" if avg_confidence >= 0.4 else "danger"
                        )
                    ], width=6),
                    dbc.Col([
                        html.H6("Confident Mappings"),
                        html.H3(f"{confident_mappings}/{total_columns}",
                               className="text-success" if confident_mappings >= total_columns * 0.7 else "text-warning")
                    ], width=6)
                ])
            ])
        ], className="mb-3")
        
        # Suggestions table
        table_rows = []
        for suggestion in suggestions:
            confidence = suggestion['confidence']
            row_color = "table-success" if confidence >= 0.7 else "table-warning" if confidence >= 0.4 else "table-danger"
            
            table_rows.append(
                html.Tr([
                    html.Td(suggestion['column']),
                    html.Td(suggestion['suggested_field']),
                    html.Td([
                        dbc.Progress(
                            value=confidence * 100,
                            label=f"{confidence:.1%}",
                            size="sm",
                            color="success" if confidence >= 0.7 else "warning" if confidence >= 0.4 else "danger"
                        )
                    ]),
                    html.Td(suggestion['status']),
                    html.Td(html.Small(str(suggestion['sample_data'][:2]), className="text-muted"))
                ], className=row_color)
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
        
        # Data preview
        data_preview = suggests_data.get("data_preview", [])
        if data_preview:
            preview_df = pd.DataFrame(data_preview)
            preview_table = dbc.Card([
                dbc.CardHeader([
                    html.H6("📊 Data Preview (First 5 rows)")
                ]),
                dbc.CardBody([
                    dbc.Table.from_dataframe(
                        preview_df,
                        responsive=True,
                        striped=True,
                        size="sm"
                    )
                ])
            ], className="mb-3")
        else:
            preview_table = html.Div()
        
        return html.Div([
            summary_card,
            suggestions_table,
            preview_table
        ])
        
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
        header = dbc.Row([
            dbc.Col([
                html.H1("🔍 Deep Analytics", className="text-primary"),
                html.P("Advanced data analysis with AI-powered column mapping suggestions",
                       className="lead text-muted"),
                dbc.Alert(
                    "✅ UI components loaded successfully",
                    color="success",
                    dismissable=True,
                    id="status-alert"
                )
            ])
        ], className="mb-4")
        
        # Configuration section
        config_card = dbc.Card([
            dbc.CardHeader([
                html.H5("⚙️ Analysis Configuration")
            ]),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Label("Data Source", className="fw-bold"),
                        dcc.Dropdown(
                            id="analytics-data-source",
                            options=get_data_source_options_safe(),
                            placeholder="Select data source...",
                            value=None
                        )
                    ], width=6),
                    dbc.Col([
                        html.Label("Analysis Type", className="fw-bold"),
                        dcc.Dropdown(
                            id="analytics-type",
                            options=get_analysis_type_options(),
                            value="suggests",
                            placeholder="Select analysis type..."
                        )
                    ], width=6)
                ], className="mb-3"),
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
        ], className="mb-4")
        
        # Results display area
        results_area = html.Div(
            id="analytics-display-area",
            children=[
                dbc.Alert(
                    [
                        html.H6("👆 Get Started"),
                        html.P("1. Select a data source (files with 🤖 have AI suggestions)"),
                        html.P("2. Choose 'AI Column Suggestions' to see mapping analysis"),
                        html.P("3. Click 'Generate Analytics' to begin")
                    ],
                    color="info"
                )
            ]
        )
        
        # Hidden stores and triggers
        stores = [
            dcc.Store(id="analytics-results-store", data={}),
            dcc.Store(id="service-health-store", data={}),
            html.Div(id="hidden-trigger", style={"display": "none"})
        ]
        
        # Complete layout
        return dbc.Container([
            header,
            config_card,
            results_area
        ] + stores, fluid=True)
        
    except Exception as e:
        logger.error(f"Critical error creating layout: {e}")
        return dbc.Container([
            dbc.Alert([
                html.H4("⚠️ Page Loading Error"),
                html.P(f"Error: {str(e)}"),
                html.P("Please check imports and dependencies.")
            ], color="danger")
        ])

# =============================================================================
# SECTION 6: CONSOLIDATED CALLBACKS
# REPLACE the existing callbacks in pages/deep_analytics.py with these
# =============================================================================

@callback(
    Output("analytics-display-area", "children"),
    [Input("generate-analytics-btn", "n_clicks")],
    [State("analytics-data-source", "value"),
     State("analytics-type", "value")],
    prevent_initial_call=True
)
def consolidated_analytics_callback(n_clicks, data_source, analysis_type):
    """
    CONSOLIDATED CALLBACK - Replace existing analytics callbacks
    
    INTEGRATION INSTRUCTIONS:
    1. Find existing callbacks that update analytics display
    2. Replace them with this single consolidated callback
    3. Remove duplicate callback functions
    """
    if not n_clicks or not data_source or data_source == "none":
        return dbc.Alert("Please select a valid data source", color="warning")
    
    try:
        # Loading indicator
        loading_content = [
            dbc.Spinner([
                html.H5("🔄 Processing..."),
                html.P(f"Analyzing {data_source} for {analysis_type} patterns")
            ], color="primary")
        ]
        
        # Process based on analysis type
        if analysis_type == "suggests":
            # Handle suggests analysis
            suggests_data = process_suggests_analysis(data_source)
            return create_suggests_display(suggests_data)
            
        elif analysis_type in ["security", "trends", "behavior", "anomaly"]:
            # Handle other analysis types
            try:
                service = get_analytics_service_safe()
                if service:
                    # Use service for analysis
                    results = service.analyze_data(data_source, analysis_type)
                    return create_analysis_results_display(results, analysis_type)
                else:
                    return create_limited_analysis_display(data_source, analysis_type)
            except Exception as e:
                return dbc.Alert(f"Analysis failed: {str(e)}", color="danger")
                
        elif analysis_type == "quality":
            # Handle data quality analysis
            return create_data_quality_display(data_source)
            
        else:
            return dbc.Alert(f"Analysis type '{analysis_type}' not supported", color="warning")
            
    except Exception as e:
        logger.error(f"Analytics callback error: {e}")
        return dbc.Alert(f"Error: {str(e)}", color="danger")

@callback(
    Output("analytics-data-source", "options"),
    Input("refresh-sources-btn", "n_clicks"),
    prevent_initial_call=True
)
def refresh_data_sources_callback(n_clicks):
    """Refresh data sources when button clicked"""
    if n_clicks:
        return get_data_source_options_safe()
    return get_data_source_options_safe()

@callback(
    Output("status-alert", "children"),
    Input("hidden-trigger", "children"),
    prevent_initial_call=False
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

def create_analysis_results_display(results: Dict[str, Any], analysis_type: str) -> html.Div:
    """Create display for standard analysis results"""
    try:
        return dbc.Card([
            dbc.CardHeader([
                html.H5(f"📊 {analysis_type.title()} Analysis Results")
            ]),
            dbc.CardBody([
                html.P(f"Analysis completed for {analysis_type} patterns."),
                html.P(f"Found {results.get('total_events', 0)} events to analyze."),
                html.P("Detailed results would be displayed here.")
            ])
        ])
    except Exception as e:
        return dbc.Alert(f"Error displaying results: {str(e)}", color="danger")

def create_limited_analysis_display(data_source: str, analysis_type: str) -> html.Div:
    """Create limited analysis display when service unavailable"""
    return dbc.Card([
        dbc.CardHeader([
            html.H5(f"⚠️ Limited {analysis_type.title()} Analysis")
        ]),
        dbc.CardBody([
            dbc.Alert([
                html.H6("Service Limitations"),
                html.P("Full analytics service is not available."),
                html.P("Basic analysis results would be shown here.")
            ], color="warning"),
            html.P(f"Data source: {data_source}"),
            html.P(f"Analysis type: {analysis_type}")
        ])
    ])

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
                
                return dbc.Card([
                    dbc.CardHeader([
                        html.H5("📊 Data Quality Analysis")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Dataset Overview"),
                                html.P(f"Rows: {total_rows:,}"),
                                html.P(f"Columns: {total_cols}"),
                                html.P(f"Missing values: {missing_values:,}"),
                                html.P(f"Duplicate rows: {duplicate_rows:,}")
                            ], width=6),
                            dbc.Col([
                                html.H6("Quality Score"),
                                dbc.Progress(
                                    value=max(0, 100 - (missing_values/total_rows*100) - (duplicate_rows/total_rows*10)),
                                    label="Quality",
                                    color="success"
                                )
                            ], width=6)
                        ])
                    ])
                ])
        return dbc.Alert("Data quality analysis only available for uploaded files", color="info")
    except Exception as e:
        return dbc.Alert(f"Quality analysis error: {str(e)}", color="danger")

