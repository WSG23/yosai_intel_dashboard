# pages/deep_analytics.py - FIXED: No register_page at import time
"""
Deep Analytics page for Yōsai Intel Dashboard
FIXED: Removed dash.register_page() call to prevent import-time errors
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, State, no_update
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
        AnalyticsGenerator
    )
    ANALYTICS_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Analytics components not fully available: {e}")
    ANALYTICS_COMPONENTS_AVAILABLE = False
    
    # Create fallback functions
    def create_file_uploader(*args, **kwargs):
        return html.Div("File uploader not available")
    
    def create_data_preview(*args, **kwargs):
        return html.Div("Data preview not available")
    
    def create_analytics_charts(*args, **kwargs):
        return html.Div("Charts not available")
    
    def create_summary_cards(*args, **kwargs):
        return html.Div("Summary cards not available")
    
    class FileProcessor:
        @staticmethod
        def process_file_content(contents, filename):
            return None
        @staticmethod
        def validate_dataframe(df):
            return False, "FileProcessor not available", []
    
    class AnalyticsGenerator:
        @staticmethod
        def generate_analytics(df):
            return {}

def layout():
    """Deep Analytics page layout - FIXED: Now a function, no register_page call"""
    return dbc.Container([
        # Page header
        dbc.Row([
            dbc.Col([
                html.H1("🔍 Deep Analytics", className="text-primary mb-0"),
                html.P("Advanced data analysis and visualization for security intelligence", 
                      className="text-secondary mb-4")
            ])
        ]),
        
        # File upload section
        dbc.Row([
            dbc.Col([
                create_file_uploader('analytics-file-upload')
            ])
        ]),
        
        # Data storage for uploaded files
        dcc.Store(id='uploaded-data-store', data={}),
        
        # Results section
        html.Div(id='analytics-results', children=[])
        
    ], fluid=True, className="p-4")

def register_analytics_callbacks(app):
    """Register analytics page callbacks - called after app creation"""
    
    if not ANALYTICS_COMPONENTS_AVAILABLE:
        print("Warning: Analytics callbacks not registered - components not available")
        return

    @app.callback(
        [Output('upload-status', 'children'),
         Output('uploaded-data-store', 'data'),
         Output('analytics-results', 'children')],
        Input('analytics-file-upload', 'contents'),
        State('analytics-file-upload', 'filename'),
        prevent_initial_call=True
    )
    def process_uploaded_files(
        contents_list: Optional[Union[str, List[str]]], 
        filename_list: Optional[Union[str, List[str]]]
    ) -> Tuple[List[html.Div], Dict[str, Any], List[html.Div]]:
        """Process uploaded files with proper type safety"""
        
        # Early return with proper types if no content
        if not contents_list or not filename_list:
            return [], {}, []
        
        # Ensure inputs are lists
        if isinstance(contents_list, str):
            contents_list = [contents_list]
        if isinstance(filename_list, str):
            filename_list = [filename_list]
        
        # Additional safety check
        if contents_list is None or filename_list is None:
            return [], {}, []
        
        status_messages: List[html.Div] = []
        all_data: List[Dict[str, Any]] = []
        
        # Process each uploaded file
        for contents, filename in zip(contents_list, filename_list):
            try:
                # Use the modular FileProcessor
                df = FileProcessor.process_file_content(contents, filename)
                
                if df is None:
                    status_messages.append(
                        _create_error_alert(f"Unsupported file type: {filename}")
                    )
                    continue
                
                # Validate the data
                valid, message, suggestions = FileProcessor.validate_dataframe(df)
                
                if not valid:
                    alert_div = _create_warning_alert(f"{filename}: {message}")
                    
                    if suggestions:
                        suggestions_list = html.Ul([
                            html.Li(suggestion) for suggestion in suggestions
                        ])
                        combined_alert = html.Div([alert_div, suggestions_list])
                        status_messages.append(combined_alert)
                    else:
                        status_messages.append(alert_div)
                    continue
                
                # Success message
                status_messages.append(
                    _create_success_alert(
                        f"✅ Successfully loaded {filename}: {len(df):,} rows × {len(df.columns)} columns"
                    )
                )
                
                # Store processed data
                all_data.append({
                    'filename': filename,
                    'data': df.to_dict('records'),
                    'columns': list(df.columns),
                    'rows': len(df),
                    'suggestions': suggestions
                })
                
            except Exception as e:
                status_messages.append(
                    _create_error_alert(f"Error processing {filename}: {str(e)}")
                )
        
        # Generate analytics components
        analytics_components: List[html.Div] = []
        
        if all_data:
            # Combine all uploaded data for analysis
            combined_df = _combine_uploaded_data(all_data)
            
            if not combined_df.empty:
                # Generate analytics using the modular AnalyticsGenerator
                analytics_data = AnalyticsGenerator.generate_analytics(combined_df)
                
                # Create analytics components
                analytics_components = [
                    html.Div(html.Hr()),
                    html.Div([
                        html.H3("📊 Analytics Results", className="mb-4")
                    ]),
                    html.Div(create_summary_cards(analytics_data)),
                    html.Div(create_data_preview(combined_df, f"Combined Data ({len(all_data)} files)")),
                    html.Div([
                        html.H4("📈 Visualizations", className="mb-3")
                    ]),
                    html.Div(create_analytics_charts(analytics_data))
                ]
        
        return status_messages, {'files': all_data}, analytics_components

# Helper functions
def _combine_uploaded_data(all_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Combine multiple uploaded files into a single DataFrame"""
    combined_df = pd.DataFrame()
    
    for file_data in all_data:
        try:
            file_df = pd.DataFrame(file_data['data'])
            combined_df = pd.concat([combined_df, file_df], ignore_index=True, sort=False)
        except Exception as e:
            print(f"Error combining data from {file_data.get('filename', 'unknown')}: {e}")
            continue
    
    return combined_df

def _create_success_alert(message: str) -> html.Div:
    """Create a success alert message"""
    alert = dbc.Alert([
        html.I(className="fas fa-check-circle me-2"),
        message
    ], color="success", className="mb-2")
    
    return html.Div(alert)

def _create_warning_alert(message: str) -> html.Div:
    """Create a warning alert message"""
    alert = dbc.Alert([
        html.I(className="fas fa-exclamation-triangle me-2"),
        message
    ], color="warning", className="mb-2")
    
    return html.Div(alert)

def _create_error_alert(message: str) -> html.Div:
    """Create an error alert message"""
    alert = dbc.Alert([
        html.I(className="fas fa-times-circle me-2"),
        message
    ], color="danger", className="mb-2")
    
    return html.Div(alert)

# Export the layout function and callback registration
__all__ = ['layout', 'register_analytics_callbacks']