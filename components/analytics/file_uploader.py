# components/analytics/file_uploader.py - Fixed version
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
from typing import Optional

def create_file_uploader():
    """Create file upload component for analytics page"""
    
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Data Upload & Analysis", className="mb-0"),
            html.Small("Upload CSV, JSON, or Excel files for analysis", className="text-muted")
        ]),
        dbc.CardBody([
            dcc.Upload(
                id='analytics-file-upload',
                children=html.Div([
                    html.I(className="fas fa-cloud-upload-alt fa-3x mb-3"),
                    html.H5("Drag and Drop or Click to Select Files"),
                    html.P("Supports: CSV, JSON, Excel (.xlsx, .xls)", className="text-muted"),
                    html.P("Maximum file size: 100MB", className="text-muted small")
                ]),
                style={
                    'width': '100%',
                    'height': '200px',
                    'lineHeight': '200px',
                    'borderWidth': '2px',
                    'borderStyle': 'dashed',
                    'borderRadius': '10px',
                    'textAlign': 'center',
                    'backgroundColor': '#fafafa',
                    'cursor': 'pointer'
                },
                multiple=True,
                accept='.csv,.json,.xlsx,.xls'
            ),
            html.Div(id='upload-status', className="mt-3"),
            html.Div(id='file-info', className="mt-3")
        ])
    ], className="mb-4")

# components/analytics/data_preview.py - Fixed version
import dash_bootstrap_components as dbc
from dash import html, dash_table
import pandas as pd
from typing import Optional, Dict, Any, List

def create_data_preview(df: Optional[pd.DataFrame] = None, filename: str = "") -> html.Div:
    """Create data preview component"""
    
    if df is None or df.empty:
        return html.Div([
            dbc.Alert("No data to preview", color="info", className="text-center")
        ])
    
    # Limit preview to first 100 rows and basic info
    preview_df = df.head(100).copy()
    
    # Convert DataFrame to records for DataTable
    try:
        table_data = preview_df.to_dict('records')
        # Ensure all values are JSON serializable
        for record in table_data:
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = ""
                elif not isinstance(value, (str, int, float, bool)):
                    record[key] = str(value)
    except Exception:
        table_data = []
    
    # Create column definitions
    columns = []
    for col in preview_df.columns:
        columns.append({
            "name": str(col), 
            "id": str(col), 
            "type": "text",
            "presentation": "markdown" if len(str(col)) > 20 else "input"
        })
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5(f"Data Preview: {filename}", className="mb-0"),
            html.Small(f"{len(df):,} rows × {len(df.columns)} columns", className="text-muted")
        ]),
        dbc.CardBody([
            # Data summary
            dbc.Row([
                dbc.Col([
                    html.H6("Dataset Summary"),
                    html.P(f"Total Records: {len(df):,}"),
                    html.P(f"Columns: {len(df.columns)}"),
                    html.P(f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")
                ], width=3),
                dbc.Col([
                    html.H6("Column Types"),
                    html.Div([
                        html.P(f"{str(dtype)}: {count}")
                        for dtype, count in df.dtypes.value_counts().items()
                    ])
                ], width=3),
                dbc.Col([
                    html.H6("Data Quality"),
                    html.P(f"Missing Values: {df.isnull().sum().sum():,}"),
                    html.P(f"Duplicate Rows: {df.duplicated().sum():,}"),
                    html.P(f"Unique Values: {df.nunique().sum():,}")
                ], width=3),
                dbc.Col([
                    html.H6("Date Range"),
                    html.Div(id="date-range-info", children=get_date_range_info(df))
                ], width=3)
            ], className="mb-3"),
            
            # Data table
            html.H6("Data Preview (First 100 rows)"),
            create_data_table(table_data, columns) if table_data else html.P("No data to display")
        ])
    ], className="mb-4")

def get_date_range_info(df: pd.DataFrame) -> List[html.P]:
    """Extract date range information from DataFrame"""
    date_cols = [col for col in df.columns if 'date' in str(col).lower() or 'time' in str(col).lower()]
    
    if not date_cols:
        return [html.P("No date columns found")]
    
    info = []
    for col in date_cols[:2]:  # Show max 2 date columns
        try:
            date_series = pd.to_datetime(df[col], errors='coerce')
            if not date_series.isna().all():
                min_date = date_series.min()
                max_date = date_series.max()
                info.append(html.P(f"{col}: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"))
        except Exception:
            continue
    
    return info if info else [html.P("No valid dates found")]

def create_data_table(data: List[Dict[str, Any]], columns: List[Dict[str, str]]) -> dash_table.DataTable:
    """Create a DataTable with proper styling"""
    
    return dash_table.DataTable(
        data=data,
        columns=columns,
        page_size=10,
        style_table={
            'overflowX': 'auto',
            'minWidth': '100%'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Arial',
            'fontSize': '12px',
            'maxWidth': '200px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis'
        },
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold',
            'border': '1px solid rgb(200, 200, 200)'
        },
        style_data={
            'border': '1px solid rgb(200, 200, 200)'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        filter_action="native",
        sort_action="native",
        export_format="csv"
    )

# components/analytics/analytics_charts.py - Fixed version  
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
from typing import Dict, Any, List, Optional

def create_analytics_charts(analytics_data: Dict[str, Any]) -> html.Div:
    """Create analytics visualization charts"""
    
    if not analytics_data:
        return html.Div([
            dbc.Alert("No data available for visualization", color="info", className="text-center")
        ])
    
    charts = []
    
    # Access Patterns Chart
    if 'access_patterns' in analytics_data and analytics_data['access_patterns']:
        try:
            access_fig = px.pie(
                values=list(analytics_data['access_patterns'].values()),
                names=list(analytics_data['access_patterns'].keys()),
                title="Access Result Distribution"
            )
            access_fig.update_layout(height=400, showlegend=True)
            
            charts.append(
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Access Patterns"),
                        dbc.CardBody([
                            dcc.Graph(figure=access_fig, id="access-patterns-chart")
                        ])
                    ])
                ], width=6)
            )
        except Exception as e:
            print(f"Error creating access patterns chart: {e}")
    
    # Hourly Patterns Chart
    if 'hourly_patterns' in analytics_data and analytics_data['hourly_patterns']:
        try:
            hours = list(analytics_data['hourly_patterns'].keys())
            counts = list(analytics_data['hourly_patterns'].values())
            
            hourly_fig = px.bar(
                x=hours,
                y=counts,
                title="Access Events by Hour of Day",
                labels={'x': 'Hour of Day', 'y': 'Number of Events'}
            )
            hourly_fig.update_layout(
                xaxis_title="Hour of Day",
                yaxis_title="Number of Events",
                height=400,
                xaxis=dict(tickmode='linear')
            )
            
            charts.append(
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Hourly Activity Patterns"),
                        dbc.CardBody([
                            dcc.Graph(figure=hourly_fig, id="hourly-patterns-chart")
                        ])
                    ])
                ], width=6)
            )
        except Exception as e:
            print(f"Error creating hourly patterns chart: {e}")
    
    # Top Users Chart
    if 'top_users' in analytics_data and analytics_data['top_users']:
        try:
            users = list(analytics_data['top_users'].keys())
            counts = list(analytics_data['top_users'].values())
            
            users_fig = px.bar(
                x=counts,
                y=users,
                orientation='h',
                title="Top 10 Most Active Users",
                labels={'x': 'Number of Access Events', 'y': 'User ID'}
            )
            users_fig.update_layout(
                xaxis_title="Number of Access Events",
                yaxis_title="User ID",
                height=400
            )
            
            charts.append(
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Most Active Users"),
                        dbc.CardBody([
                            dcc.Graph(figure=users_fig, id="top-users-chart")
                        ])
                    ])
                ], width=6)
            )
        except Exception as e:
            print(f"Error creating top users chart: {e}")
    
    # Top Doors Chart
    if 'top_doors' in analytics_data and analytics_data['top_doors']:
        try:
            doors = list(analytics_data['top_doors'].keys())
            counts = list(analytics_data['top_doors'].values())
            
            doors_fig = px.bar(
                x=counts,
                y=doors,
                orientation='h',
                title="Top 10 Most Used Doors",
                labels={'x': 'Number of Access Events', 'y': 'Door ID'}
            )
            doors_fig.update_layout(
                xaxis_title="Number of Access Events",
                yaxis_title="Door ID",
                height=400
            )
            
            charts.append(
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Most Active Doors"),
                        dbc.CardBody([
                            dcc.Graph(figure=doors_fig, id="top-doors-chart")
                        ])
                    ])
                ], width=6)
            )
        except Exception as e:
            print(f"Error creating top doors chart: {e}")
    
    if not charts:
        return html.Div([
            dbc.Alert("No charts available - insufficient data", color="warning", className="text-center")
        ])
    
    # Arrange charts in rows
    rows = []
    for i in range(0, len(charts), 2):
        if i + 1 < len(charts):
            rows.append(dbc.Row([charts[i], charts[i + 1]], className="mb-4"))
        else:
            rows.append(dbc.Row([charts[i]], className="mb-4"))
    
    return html.Div(rows)

def create_summary_cards(analytics_data: Dict[str, Any]) -> html.Div:
    """Create summary statistic cards"""
    
    if not analytics_data:
        return html.Div()
    
    cards = []
    
    # Total Events Card
    if 'total_events' in analytics_data:
        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{analytics_data['total_events']:,}", className="card-title text-primary"),
                        html.P("Total Events", className="card-text text-muted")
                    ])
                ], color="primary", outline=True)
            ], width=3)
        )
    
    # Date Range Card
    if 'date_range' in analytics_data and analytics_data['date_range'] and analytics_data['date_range'].get('start'):
        start_date = analytics_data['date_range']['start']
        end_date = analytics_data['date_range']['end']
        
        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6(f"{start_date}", className="card-title"),
                        html.H6(f"to {end_date}", className="card-title"),
                        html.P("Date Range", className="card-text text-muted")
                    ])
                ], color="info", outline=True)
            ], width=3)
        )
    
    # Top Users Count
    if 'top_users' in analytics_data:
        user_count = len(analytics_data['top_users'])
        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{user_count}", className="card-title text-success"),
                        html.P("Active Users", className="card-text text-muted")
                    ])
                ], color="success", outline=True)
            ], width=3)
        )
    
    # Top Doors Count
    if 'top_doors' in analytics_data:
        door_count = len(analytics_data['top_doors'])
        cards.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{door_count}", className="card-title text-warning"),
                        html.P("Active Doors", className="card-text text-muted")
                    ])
                ], color="warning", outline=True)
            ], width=3)
        )
    
    if cards:
        return dbc.Row(cards, className="mb-4")
    else:
        return html.Div()