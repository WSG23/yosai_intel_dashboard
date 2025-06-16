# pages/deep_analytics.py - Updated to use modular analytics components
import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union

# Import the new modular analytics components
from components.analytics import (
    create_file_uploader,
    create_data_preview,
    create_analytics_charts,
    create_summary_cards,
    FileProcessor,
    AnalyticsGenerator
)

# Register this page with Dash
dash.register_page(__name__, path="/analytics", title="Deep Analytics")

def layout():
    """Deep Analytics page layout using modular components"""
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

# Main callback for file upload processing
@callback(
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
    """Process uploaded files and generate analytics using modular components"""
    
    if not contents_list:
        return [], {}, []
    
    # Ensure inputs are lists
    if isinstance(contents_list, str):
        contents_list = [contents_list]
    if isinstance(filename_list, str):
        filename_list = [filename_list]
    
    status_messages = []
    all_data = []
    
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
                alert = _create_warning_alert(f"{filename}: {message}")
                if suggestions:
                    alert.children.append(html.Ul([
                        html.Li(suggestion) for suggestion in suggestions
                    ]))
                status_messages.append(alert)
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
    
    # Generate analytics if we have data
    analytics_components = []
    
    if all_data:
        # Combine all uploaded data for analysis
        combined_df = _combine_uploaded_data(all_data)
        
        if not combined_df.empty:
            # Generate analytics using the modular AnalyticsGenerator
            analytics_data = AnalyticsGenerator.generate_analytics(combined_df)
            
            # Create analytics components using modular functions
            analytics_components = [
                html.Hr(),
                html.H3("📊 Analytics Results", className="mb-4"),
                
                # Summary cards
                create_summary_cards(analytics_data),
                
                # Data preview
                create_data_preview(combined_df, f"Combined Data ({len(all_data)} files)"),
                
                # Visualizations
                html.H4("📈 Visualizations", className="mb-3"),
                create_analytics_charts(analytics_data),
                
                # Data quality section
                _create_data_quality_section(combined_df, all_data)
            ]
    
    return status_messages, {'files': all_data}, analytics_components

# Helper callback for real-time analytics updates
@callback(
    Output('analytics-results', 'children', allow_duplicate=True),
    Input('uploaded-data-store', 'data'),
    prevent_initial_call=True
)
def update_analytics_display(stored_data: Optional[Dict[str, Any]]) -> List[html.Div]:
    """Update analytics display when data changes"""
    
    if not stored_data or 'files' not in stored_data:
        return []
    
    # Recreate combined dataframe
    combined_df = _combine_uploaded_data(stored_data['files'])
    
    if combined_df.empty:
        return []
    
    # Generate analytics using modular components
    analytics_data = AnalyticsGenerator.generate_analytics(combined_df)
    
    return [
        html.Hr(),
        html.H3("📊 Analytics Results", className="mb-4"),
        create_summary_cards(analytics_data),
        create_data_preview(combined_df, f"Combined Data ({len(stored_data['files'])} files)"),
        html.H4("📈 Visualizations", className="mb-3"),
        create_analytics_charts(analytics_data)
    ]

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

def _create_success_alert(message: str) -> dbc.Alert:
    """Create a success alert message"""
    return dbc.Alert([
        html.I(className="fas fa-check-circle me-2"),
        message
    ], color="success", className="mb-2")

def _create_warning_alert(message: str) -> dbc.Alert:
    """Create a warning alert message"""
    return dbc.Alert([
        html.I(className="fas fa-exclamation-triangle me-2"),
        message
    ], color="warning", className="mb-2")

def _create_error_alert(message: str) -> dbc.Alert:
    """Create an error alert message"""
    return dbc.Alert([
        html.I(className="fas fa-times-circle me-2"),
        message
    ], color="danger", className="mb-2")

def _create_data_quality_section(df: pd.DataFrame, all_data: List[Dict[str, Any]]) -> html.Div:
    """Create a data quality assessment section"""
    
    # Calculate data quality metrics
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    completeness = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
    
    # Collect all suggestions
    all_suggestions = []
    for file_data in all_data:
        all_suggestions.extend(file_data.get('suggestions', []))
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5("🔍 Data Quality Assessment", className="mb-0")
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6("Completeness"),
                    dbc.Progress(
                        value=completeness, 
                        color="success" if completeness >= 95 else "warning" if completeness >= 80 else "danger",
                        striped=True,
                        label=f"{completeness:.1f}%"
                    )
                ], width=4),
                dbc.Col([
                    html.H6("Missing Values"),
                    html.P(f"{missing_cells:,} out of {total_cells:,} cells", className="text-muted")
                ], width=4),
                dbc.Col([
                    html.H6("Data Types"),
                    html.Div([
                        html.Small(f"{dtype}: {count}", className="d-block")
                        for dtype, count in df.dtypes.value_counts().items()
                    ])
                ], width=4)
            ]),
            
            # Show suggestions if any
            html.Hr() if all_suggestions else html.Div(),
            html.H6("💡 Suggestions", className="mt-3") if all_suggestions else html.Div(),
            html.Ul([
                html.Li(suggestion) for suggestion in all_suggestions[:5]  # Show top 5
            ]) if all_suggestions else html.Div()
        ])
    ], className="mb-4")

# Export layout function for external use
__all__ = ['layout']