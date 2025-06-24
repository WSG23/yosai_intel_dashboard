"""
Column Data Presenter Module
Modular component for displaying column data after mapping verification
"""

import pandas as pd
from dash import html, dcc, dash_table
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ColumnDataPresenter:
    """Handles presentation of column data after mapping completion"""
    
    def __init__(self, max_preview_rows: int = 10):
        self.max_preview_rows = max_preview_rows
    
    def create_column_summary_table(self, data: List[Dict], mapping: Dict[str, str]) -> html.Div:
        """Create a summary table showing mapped columns and their data types"""
        try:
            df = pd.DataFrame(data)
            summary_data = []
            
            for mapped_field, column_name in mapping.items():
                if column_name in df.columns:
                    col_data = df[column_name]
                    summary_data.append({
                        'Field': mapped_field.title(),
                        'Column': column_name,
                        'Data Type': str(col_data.dtype),
                        'Non-Null Count': col_data.count(),
                        'Sample Value': str(col_data.dropna().iloc[0]) if not col_data.dropna().empty else 'N/A'
                    })
            
            return html.Div([
                html.H4("\ud83d\udcca Column Mapping Summary", className="text-lg font-semibold mb-3"),
                dash_table.DataTable(
                    data=summary_data,
                    columns=[
                        {"name": "Field", "id": "Field"},
                        {"name": "Source Column", "id": "Column"},
                        {"name": "Data Type", "id": "Data Type"},
                        {"name": "Records", "id": "Non-Null Count"},
                        {"name": "Sample", "id": "Sample Value"}
                    ],
                    style_cell={'textAlign': 'left', 'padding': '10px'},
                    style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                    style_data={'backgroundColor': 'rgb(248, 249, 250)'}
                )
            ], className="mb-6")
            
        except Exception as e:
            logger.error(f"Error creating column summary: {e}")
            return html.Div("Error creating column summary", className="text-red-600")
    
    def create_data_preview_table(self, data: List[Dict], mapping: Dict[str, str]) -> html.Div:
        """Create a preview table showing actual data with mapped columns highlighted"""
        try:
            df = pd.DataFrame(data)
            preview_df = df.head(self.max_preview_rows)
            
            # Prepare columns for display, highlighting mapped ones
            columns = []
            for col in preview_df.columns:
                is_mapped = col in mapping.values()
                mapped_field = next((k for k, v in mapping.items() if v == col), None)
                
                col_config = {
                    "name": f"\ud83c\udfaf {col} ({mapped_field})" if is_mapped else col,
                    "id": col
                }
                columns.append(col_config)
            
            return html.Div([
                html.H4("\ud83d\udd0d Data Preview", className="text-lg font-semibold mb-3"),
                html.P(f"Showing first {len(preview_df)} of {len(df)} records", 
                       className="text-sm text-gray-600 mb-2"),
                dash_table.DataTable(
                    data=preview_df.to_dict('records'),
                    columns=columns,
                    style_cell={'textAlign': 'left', 'padding': '8px', 'fontSize': '12px'},
                    style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
                    style_data_conditional=[
                        {
                            'if': {'column_id': col},
                            'backgroundColor': 'rgb(220, 252, 231)',
                            'border': '1px solid rgb(34, 197, 94)'
                        } for col in mapping.values()
                    ],
                    page_size=self.max_preview_rows,
                    fixed_rows={'headers': True}
                )
            ], className="mb-6")
            
        except Exception as e:
            logger.error(f"Error creating data preview: {e}")
            return html.Div("Error creating data preview", className="text-red-600")
    
    def create_validation_status(self, data: List[Dict], mapping: Dict[str, str]) -> html.Div:
        """Create validation status component showing data quality metrics"""
        try:
            df = pd.DataFrame(data)
            issues = []
            
            for field, column in mapping.items():
                if column in df.columns:
                    col_data = df[column]
                    null_count = col_data.isnull().sum()
                    null_percentage = (null_count / len(df)) * 100
                    
                    if null_percentage > 10:
                        issues.append(f"{field}: {null_percentage:.1f}% missing values")
                    
                    # Check for common data issues
                    if field == 'timestamp' and not pd.api.types.is_datetime64_any_dtype(col_data):
                        issues.append(f"{field}: Non-datetime format detected")
            
            status_color = "text-green-600" if not issues else "text-yellow-600"
            status_icon = "\u2705" if not issues else "\u26a0\ufe0f"
            
            return html.Div([
                html.H4("\ud83d\udd0e Data Validation", className="text-lg font-semibold mb-3"),
                html.Div([
                    html.P(f"{status_icon} Data Quality Status", className=f"{status_color} font-medium"),
                    html.Ul([
                        html.Li(issue, className="text-sm text-yellow-700") 
                        for issue in issues
                    ]) if issues else html.P("All mapped columns look good!", className="text-green-600 text-sm")
                ], className="p-3 bg-gray-50 rounded")
            ], className="mb-6")
            
        except Exception as e:
            logger.error(f"Error creating validation status: {e}")
            return html.Div("Error validating data", className="text-red-600")
    
    def generate_complete_presentation(self, data: List[Dict], mapping: Dict[str, str], 
                                     filename: str = "") -> html.Div:
        """Generate the complete column data presentation after mapping"""
        try:
            return html.Div([
                # Header
                html.Div([
                    html.H3("\u2728 Column Data Presentation", className="text-xl font-bold mb-2"),
                    html.P(f"File: {filename}" if filename else "Uploaded Data", 
                           className="text-gray-600 mb-4")
                ]),
                
                # Components
                self.create_column_summary_table(data, mapping),
                self.create_validation_status(data, mapping),
                self.create_data_preview_table(data, mapping),
                
                # Action buttons
                html.Div([
                    html.Button("\u2705 Proceed to Device Mapping", 
                               id="proceed-to-device-btn",
                               className="btn btn-primary mr-3"),
                    html.Button("\ud83d\udd04 Revise Mapping", 
                               id="revise-mapping-btn",
                               className="btn btn-secondary")
                ], className="mt-4 text-center")
                
            ], className="column-data-presentation p-4 bg-white rounded-lg shadow")
            
        except Exception as e:
            logger.error(f"Error generating complete presentation: {e}")
            return html.Div(f"Error presenting data: {str(e)}", className="text-red-600")


def create_column_data_presenter(max_preview_rows: int = 10) -> ColumnDataPresenter:
    """Factory function to create ColumnDataPresenter instance"""
    return ColumnDataPresenter(max_preview_rows=max_preview_rows)
