# pages/deep_analytics.py - FIXED: Type-safe version with all Pylance errors resolved
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

# FIXED: Main callback with proper type annotations and null checking
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
    """FIXED: Process uploaded files with proper type safety"""
    
    # FIXED: Early return with proper types if no content
    if not contents_list or not filename_list:
        return [], {}, []
    
    # FIXED: Ensure inputs are lists with proper null checking
    if isinstance(contents_list, str):
        contents_list = [contents_list]
    if isinstance(filename_list, str):
        filename_list = [filename_list]
    
    # FIXED: Additional safety check for None values
    if contents_list is None or filename_list is None:
        return [], {}, []
    
    status_messages: List[html.Div] = []
    all_data: List[Dict[str, Any]] = []
    
    # FIXED: Process each uploaded file with proper iteration
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
                
                # FIXED: Proper handling of suggestions with type safety
                if suggestions:
                    suggestions_list = html.Ul([
                        html.Li(suggestion) for suggestion in suggestions
                    ])
                    # FIXED: Create a new div that combines alert and suggestions
                    combined_alert = html.Div([
                        alert_div,
                        suggestions_list
                    ])
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
    
    # FIXED: Generate analytics with proper return type
    analytics_components: List[html.Div] = []
    
    if all_data:
        # Combine all uploaded data for analysis
        combined_df = _combine_uploaded_data(all_data)
        
        if not combined_df.empty:
            # Generate analytics using the modular AnalyticsGenerator
            analytics_data = AnalyticsGenerator.generate_analytics(combined_df)
            
            # FIXED: Create analytics components with proper typing
            analytics_components = [
                html.Div(html.Hr()),  # Wrap Hr in Div
                html.Div([
                    html.H3("📊 Analytics Results", className="mb-4")
                ]),
                
                # Summary cards (already returns html.Div)
                html.Div(create_summary_cards(analytics_data)),
                
                # Data preview (already returns html.Div)
                html.Div(create_data_preview(combined_df, f"Combined Data ({len(all_data)} files)")),
                
                # Visualizations
                html.Div([
                    html.H4("📈 Visualizations", className="mb-3")
                ]),
                html.Div(create_analytics_charts(analytics_data)),
                
                # Data quality section
                html.Div(_create_data_quality_section(combined_df, all_data))
            ]
    
    return status_messages, {'files': all_data}, analytics_components

# FIXED: Helper callback with proper return type
@callback(
    Output('analytics-results', 'children', allow_duplicate=True),
    Input('uploaded-data-store', 'data'),
    prevent_initial_call=True
)
def update_analytics_display(stored_data: Optional[Dict[str, Any]]) -> List[html.Div]:
    """FIXED: Update analytics display when data changes"""
    
    if not stored_data or 'files' not in stored_data:
        return []
    
    # Recreate combined dataframe
    combined_df = _combine_uploaded_data(stored_data['files'])
    
    if combined_df.empty:
        return []
    
    # Generate analytics using modular components
    analytics_data = AnalyticsGenerator.generate_analytics(combined_df)
    
    # FIXED: Return proper List[html.Div] type
    return [
        html.Div(html.Hr()),
        html.Div([
            html.H3("📊 Analytics Results", className="mb-4")
        ]),
        html.Div(create_summary_cards(analytics_data)),
        html.Div(create_data_preview(combined_df, f"Combined Data ({len(stored_data['files'])} files)")),
        html.Div([
            html.H4("📈 Visualizations", className="mb-3")
        ]),
        html.Div(create_analytics_charts(analytics_data))
    ]

# FIXED: Helper functions with proper return types

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
    """FIXED: Create a success alert message wrapped in Div"""
    alert = dbc.Alert([
        html.I(className="fas fa-check-circle me-2"),
        message
    ], color="success", className="mb-2")
    
    return html.Div(alert)

def _create_warning_alert(message: str) -> html.Div:
    """FIXED: Create a warning alert message wrapped in Div"""
    alert = dbc.Alert([
        html.I(className="fas fa-exclamation-triangle me-2"),
        message
    ], color="warning", className="mb-2")
    
    return html.Div(alert)

def _create_error_alert(message: str) -> html.Div:
    """FIXED: Create an error alert message wrapped in Div"""
    alert = dbc.Alert([
        html.I(className="fas fa-times-circle me-2"),
        message
    ], color="danger", className="mb-2")
    
    return html.Div(alert)

def _create_data_quality_section(df: pd.DataFrame, all_data: List[Dict[str, Any]]) -> html.Div:
    """FIXED: Create a data quality assessment section that returns html.Div"""
    
    # Calculate data quality metrics
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    completeness = ((total_cells - missing_cells) / total_cells * 100) if total_cells > 0 else 0
    
    # Collect all suggestions
    all_suggestions: List[str] = []
    for file_data in all_data:
        all_suggestions.extend(file_data.get('suggestions', []))
    
    # FIXED: Return html.Div containing the card
    card = dbc.Card([
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
    
    return html.Div(card)

# Export layout function for external use
__all__ = ['layout']