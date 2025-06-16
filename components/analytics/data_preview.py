# components/analytics/data_preview.py - Type-safe version
import dash_bootstrap_components as dbc
from dash import html, dash_table
import pandas as pd
from typing import Optional

def create_data_preview(df: Optional[pd.DataFrame] = None, filename: str = "") -> html.Div:
    """Create data preview component - type-safe version"""
    
    if df is None or df.empty:
        return html.Div([
            dbc.Alert("No data to preview", color="info", className="text-center")
        ])
    
    # Simple, type-safe data processing
    preview_df = df.head(50).copy()
    
    # Convert all data to strings for type safety
    table_data = []
    for _, row in preview_df.iterrows():
        row_dict = {}
        for col in preview_df.columns:
            value = row[col]
            row_dict[str(col)] = "" if pd.isna(value) else str(value)
        table_data.append(row_dict)
    
    # Simple column definitions
    columns = [{"name": str(col), "id": str(col)} for col in preview_df.columns]
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5(f"Data Preview: {filename}", className="mb-0"),
                html.Small(f"{len(df):,} rows × {len(df.columns)} columns", className="text-muted")
            ]),
            dbc.CardBody([
                html.P(f"Showing first {len(preview_df)} rows"),
                
                dash_table.DataTable(
                    data=table_data,
                    columns=columns,
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'left', 'padding': '8px'},
                    style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'}
                ) if table_data else html.P("No data to display")
            ])
        ], className="mb-4")
    ])
