# components/analytics/data_preview.py - FIXED: Proper exports
"""
Data preview component for analytics page
FIXED: Properly exports create_data_preview function
"""

try:
    import dash_bootstrap_components as dbc
    from dash import html
    import pandas as pd
    from typing import Optional, List
    DASH_AVAILABLE = True
except ImportError:
    print("Warning: Dash components not available in data_preview")
    DASH_AVAILABLE = False
    # Create fallback types
    dbc = None
    html = None
    pd = None

from typing import Any

def create_data_preview(df: Optional[pd.DataFrame] = None, filename: str = "") -> Any:
    """Create data preview component - FIXED: Properly exported function"""

    if not DASH_AVAILABLE or html is None or dbc is None:
        if html is not None:
            return html.Div("Data preview not available - Dash not installed")
        return None
    
    if df is None or df.empty:
        return html.Div([
            dbc.Alert("No data to preview", color="info", className="text-center")
        ])
    
    # Simple, type-safe data processing
    preview_df = df.head(50).copy()
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5(f"Data Preview: {filename}", className="mb-0"),
                html.Div(f"{len(df):,} rows × {len(df.columns)} columns", className="text-muted small")
            ]),
            dbc.CardBody([
                html.Div(f"Showing first {len(preview_df)} rows", className="mb-3"),
                
                # Use simple HTML table - guaranteed type safety
                _create_type_safe_table(preview_df) if not preview_df.empty else html.Div("No data to display", className="text-muted")
            ])
        ], className="mb-4")
    ])

def _create_type_safe_table(df: pd.DataFrame) -> Any:
    """Create a completely type-safe HTML table"""

    if not DASH_AVAILABLE or html is None or dbc is None or pd is None or df.empty:
        if html is not None:
            return html.Div("No data available", className="text-muted")
        return None
    
    # Limit for performance and display
    max_cols = 8
    max_rows = 15
    
    display_df = df.iloc[:max_rows, :max_cols]
    
    # Build table components step by step with explicit typing
    
    # 1. Header cells
    header_cells: List[Any] = []
    for col in display_df.columns:
        col_name = str(col)
        display_name = col_name[:25] + "..." if len(col_name) > 25 else col_name
        header_cells.append(
            html.Th(display_name, className="table-header")
        )
    
    # 2. Header row
    header_row = html.Tr(header_cells)
    table_header = html.Thead([header_row], className="table-dark")
    
    # 3. Body rows
    body_rows: List[Any] = []
    for row_idx, (_, row) in enumerate(display_df.iterrows()):
        
        # Build cells for this row
        row_cells: List[Any] = []
        for col in display_df.columns:
            cell_value = row[col]
            
            # Safe value conversion
            if pd.isna(cell_value):
                display_value = ""
                cell_class = "text-muted"
            elif isinstance(cell_value, (int, float)):
                display_value = str(cell_value)
                cell_class = "text-end"
            else:
                str_value = str(cell_value)
                display_value = str_value[:40] + "..." if len(str_value) > 40 else str_value
                cell_class = ""
            
            row_cells.append(
                html.Td(
                    display_value,
                    className=f"table-cell {cell_class}",
                    title=str(cell_value) if not pd.isna(cell_value) else "Empty"
                )
            )
        
        # Create row with alternating style
        row_class = "table-row-alt" if row_idx % 2 == 1 else ""
        body_rows.append(html.Tr(row_cells, className=row_class))
    
    # 4. Table body
    table_body = html.Tbody(body_rows)
    
    # 5. Complete table
    complete_table = html.Table(
        [table_header, table_body],
        className="table table-striped table-hover table-sm table-bordered",
        style={
            'fontSize': '0.8rem',
            'marginBottom': '0',
            'backgroundColor': 'white'
        }
    )
    
    # 6. Scrollable container
    table_container = html.Div(
        [complete_table],
        style={
            'overflowX': 'auto',
            'overflowY': 'auto',
            'maxHeight': '350px',
            'border': '1px solid #ddd',
            'borderRadius': '4px',
            'backgroundColor': 'white'
        }
    )
    
    # 7. Info section
    info_parts: List[str] = []
    if len(df.columns) > max_cols:
        info_parts.append(f"Showing {max_cols} of {len(df.columns)} columns")
    if len(df) > max_rows:
        info_parts.append(f"Showing {max_rows} of {len(df)} rows")
    
    # 8. Build final component
    result_components: List[Any] = [
        html.Div([table_container])
    ]
    
    if info_parts:
        info_text = " • ".join(info_parts)
        info_component = html.Div(
            info_text,
            className="text-muted mt-2",
            style={'fontSize': '0.85rem'}
        )
        result_components.append(info_component)
    
    return html.Div(result_components)

def create_dataset_summary(df: pd.DataFrame) -> Any:
    """Create dataset summary with guaranteed type safety"""

    if not DASH_AVAILABLE or html is None or dbc is None or pd is None or df.empty:
        if html is not None:
            return html.Div("No data to summarize", className="text-muted")
        return None
    
    # Calculate basic stats
    total_rows = len(df)
    total_cols = len(df.columns)
    memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
    missing_count = df.isnull().sum().sum()
    total_cells = total_rows * total_cols
    missing_pct = (missing_count / total_cells * 100) if total_cells > 0 else 0
    
    # Data types count
    dtype_counts = df.dtypes.value_counts()
    dtype_text = ", ".join([f"{str(dtype)}: {count}" for dtype, count in dtype_counts.items()])
    
    # Build summary using only html.Div components
    summary_items: List[Any] = [
        html.Div(f"📊 Dimensions: {total_rows:,} rows × {total_cols} columns"),
        html.Div(f"💾 Memory Usage: {memory_mb:.1f} MB"),
        html.Div(f"❓ Missing Values: {missing_count:,} ({missing_pct:.1f}%)"),
        html.Div(f"🏷️ Data Types: {dtype_text}")
    ]
    
    return html.Div([
        html.Div("Dataset Summary", className="fw-bold mb-2"),
        html.Div(summary_items, className="summary-list text-muted", style={'fontSize': '0.9rem'})
    ])

def create_enhanced_preview(df: Optional[pd.DataFrame] = None, filename: str = "") -> Any:
    """Enhanced preview with summary - completely type safe"""

    if not DASH_AVAILABLE or html is None or dbc is None or pd is None:
        if html is not None:
            return html.Div("Enhanced preview not available - Dash not installed")
        return None
    
    if df is None or df.empty:
        return html.Div([
            dbc.Alert("No data available for preview", color="info", className="text-center")
        ])
    
    return html.Div([
        dbc.Card([
            dbc.CardHeader([
                html.H5("Data Analysis Preview", className="mb-0") if not filename else html.H5(f"Preview: {filename}", className="mb-0")
            ]),
            dbc.CardBody([
                # Summary section
                create_dataset_summary(df),
                
                # Separator
                html.Hr(className="my-3"),
                
                # Data table
                _create_type_safe_table(df)
            ])
        ], className="mb-4")
    ])

# FIXED: Explicitly export the main function
__all__ = ['create_data_preview', 'create_enhanced_preview', 'create_dataset_summary']
