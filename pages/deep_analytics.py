# pages/deep_analytics.py - Fixed version
import dash
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import base64
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union
import io

# Import your new components
#from components.analytics.file_uploader import create_file_uploader
#from components.analytics.data_preview import create_data_preview
#from components.analytics.analytics_charts import create_analytics_charts, create_summary_cards

# Register this page with Dash
dash.register_page(__name__, path="/analytics", title="Deep Analytics")

def layout():
    """Temporary analytics page layout"""
    return dbc.Container([
        html.H1("Deep Analytics - Coming Soon", className="text-primary"),
        html.P("Analytics features will be added here.", className="text-secondary")
    ], fluid=True, className="p-4")

# Callback for file upload processing
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
    """Process uploaded files and generate analytics"""
    
    if not contents_list:
        return [], {}, []
    
    # Ensure inputs are lists
    if isinstance(contents_list, str):
        contents_list = [contents_list]
    if isinstance(filename_list, str):
        filename_list = [filename_list]
    
    results = []
    all_data = []
    
    for contents, filename in zip(contents_list, filename_list):
        try:
            # Decode the file
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Process different file types
            df = process_file_content(decoded, filename)
            
            if df is None:
                results.append(
                    dbc.Alert(f"Unsupported file type: {filename}", color="danger")
                )
                continue
            
            # Basic validation
            if df.empty:
                results.append(
                    dbc.Alert(f"File {filename} is empty", color="warning")
                )
                continue
            
            # Success message
            results.append(
                dbc.Alert([
                    html.I(className="fas fa-check-circle me-2"),
                    f"Successfully uploaded {filename}: {len(df):,} rows × {len(df.columns)} columns"
                ], color="success")
            )
            
            # Store data for analytics
            all_data.append({
                'filename': filename,
                'data': df.to_dict('records'),
                'columns': list(df.columns),
                'rows': len(df)
            })
            
        except Exception as e:
            results.append(
                dbc.Alert([
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    f"Error processing {filename}: {str(e)}"
                ], color="danger")
            )
    
    # Generate analytics if we have data
    analytics_components = []
    
    if all_data:
        # Combine all uploaded data for analysis
        combined_df = combine_uploaded_data(all_data)
        
        if not combined_df.empty:
            # Generate basic analytics
            analytics_data = generate_basic_analytics(combined_df)
            
            # Create analytics components
            analytics_components = [
                html.Hr(),
                html.H3("Analytics Results", className="mb-4"),
                
                # Summary cards
                create_summary_cards(analytics_data),
                
                # Data preview
                create_data_preview(combined_df, f"Combined Data ({len(all_data)} files)"),
                
                # Charts
                html.H4("Visualizations", className="mb-3"),
                create_analytics_charts(analytics_data)
            ]
    
    return results, {'files': all_data}, analytics_components

def process_file_content(decoded: bytes, filename: str) -> Optional[pd.DataFrame]:
    """Process file content based on file type"""
    
    try:
        if filename.endswith('.csv'):
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(io.StringIO(decoded.decode(encoding)))
                    break
                except UnicodeDecodeError:
                    continue
            else:
                return None
                
        elif filename.endswith('.json'):
            try:
                json_data = json.loads(decoded.decode('utf-8'))
                if isinstance(json_data, list):
                    df = pd.DataFrame(json_data)
                elif isinstance(json_data, dict):
                    if 'data' in json_data:
                        df = pd.DataFrame(json_data['data'])
                    else:
                        df = pd.DataFrame([json_data])
                else:
                    return None
            except json.JSONDecodeError:
                return None
                
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(decoded))
            
        else:
            return None
        
        # Clean column names
        df.columns = df.columns.astype(str)
        
        return df
        
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return None

def combine_uploaded_data(all_data: List[Dict[str, Any]]) -> pd.DataFrame:
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

def generate_basic_analytics(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate basic analytics from dataframe"""
    
    if df.empty:
        return {}
    
    analytics = {
        'total_events': len(df),
        'processed_at': datetime.now().isoformat()
    }
    
    # Date range analysis
    date_columns = [col for col in df.columns if any(keyword in str(col).lower() for keyword in ['date', 'time', 'timestamp'])]
    if date_columns:
        date_col = date_columns[0]
        try:
            df_copy = df.copy()
            df_copy[date_col] = pd.to_datetime(df_copy[date_col], errors='coerce')
            valid_dates = df_copy[date_col].dropna()
            
            if not valid_dates.empty:
                analytics['date_range'] = {
                    'start': valid_dates.min().strftime('%Y-%m-%d'),
                    'end': valid_dates.max().strftime('%Y-%m-%d')
                }
                
                # Hourly patterns
                df_copy['hour'] = valid_dates.dt.hour
                hourly_counts = df_copy['hour'].value_counts().sort_index()
                analytics['hourly_patterns'] = {str(k): int(v) for k, v in hourly_counts.items()}
        except Exception as e:
            print(f"Error processing date column {date_col}: {e}")
    
    # Access patterns
    access_columns = [col for col in df.columns if any(keyword in str(col).lower() for keyword in ['access', 'result', 'status', 'outcome'])]
    if access_columns:
        access_col = access_columns[0]
        try:
            access_counts = df[access_col].value_counts()
            analytics['access_patterns'] = {str(k): int(v) for k, v in access_counts.items()}
        except Exception as e:
            print(f"Error processing access column {access_col}: {e}")
    
    # Top users
    user_columns = [col for col in df.columns if any(keyword in str(col).lower() for keyword in ['user', 'person', 'employee', 'id'])]
    if user_columns:
        user_col = user_columns[0]
        try:
            user_counts = df[user_col].value_counts().head(10)
            analytics['top_users'] = {str(k): int(v) for k, v in user_counts.items()}
        except Exception as e:
            print(f"Error processing user column {user_col}: {e}")
    
    # Top doors/locations
    door_columns = [col for col in df.columns if any(keyword in str(col).lower() for keyword in ['door', 'location', 'device', 'reader', 'point'])]
    if door_columns:
        door_col = door_columns[0]
        try:
            door_counts = df[door_col].value_counts().head(10)
            analytics['top_doors'] = {str(k): int(v) for k, v in door_counts.items()}
        except Exception as e:
            print(f"Error processing door column {door_col}: {e}")
    
    return analytics

# Additional callback for data refresh (optional)
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
    combined_df = combine_uploaded_data(stored_data['files'])
    
    if combined_df.empty:
        return []
    
    # Generate analytics
    analytics_data = generate_basic_analytics(combined_df)
    
    return [
        html.Hr(),
        html.H3("Analytics Results", className="mb-4"),
        create_summary_cards(analytics_data),
        create_data_preview(combined_df, f"Combined Data ({len(stored_data['files'])} files)"),
        html.H4("Visualizations", className="mb-3"),
        create_analytics_charts(analytics_data)
    ]