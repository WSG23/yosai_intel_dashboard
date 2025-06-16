# components/analytics/data_preview.py - Data preview component with proper typing
import dash_bootstrap_components as dbc
from dash import html, dash_table
import pandas as pd
from typing import Optional, Dict, Any, List, Union

def create_data_preview(df: Optional[pd.DataFrame] = None, filename: str = "") -> html.Div:
    """Create data preview component with proper type handling"""
    
    if df is None or df.empty:
        return html.Div([
            dbc.Alert("No data to preview", color="info", className="text-center")
        ])
    
    # Limit preview to first 100 rows
    preview_df = df.head(100).copy()
    
    # Convert DataFrame to records with proper type handling
    try:
        table_data = []
        for _, row in preview_df.iterrows():
            record = {}
            for col in preview_df.columns:
                value = row[col]
                # Ensure all values are serializable
                if pd.isna(value):
                    record[str(col)] = ""
                elif isinstance(value, (int, float, str, bool)):
                    record[str(col)] = value
                else:
                    record[str(col)] = str(value)
            table_data.append(record)
    except Exception as e:
        print(f"Error processing data: {e}")
        table_data = []
    
    # Create column definitions with proper typing
    columns = []
    for col in preview_df.columns:
        columns.append({
            "name": str(col), 
            "id": str(col),
            "type": "text"
        })
    
    return dbc.Card([
        dbc.CardHeader([
            html.H5(f"Data Preview: {filename}", className="mb-0"),
            html.Small(f"{len(df):,} rows × {len(df.columns)} columns", className="text-muted")
        ]),
        dbc.CardBody([
            # Data summary
            _create_data_summary(df),
            
            # Data table
            html.H6("Data Preview (First 100 rows)", className="mt-4 mb-3"),
            _create_data_table(table_data, columns) if table_data else html.P("No data to display")
        ])
    ], className="mb-4")

def _create_data_summary(df: pd.DataFrame) -> dbc.Row:
    """Create data summary section"""
    return dbc.Row([
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
            html.Div(id="date-range-info", children=_get_date_range_info(df))
        ], width=3)
    ], className="mb-3")

def _get_date_range_info(df: pd.DataFrame) -> List[html.P]:
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

def _create_data_table(data: List[Dict[str, Any]], columns: List[Dict[str, str]]) -> dash_table.DataTable:
    """Create a DataTable with proper typing and styling"""
    
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