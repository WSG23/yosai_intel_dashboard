"""
Analytics Generator - Creates analytics from DataFrames
"""

import pandas as pd
import json
from typing import Dict, Any, Optional

class AnalyticsGenerator:
    """Generate analytics from uploaded data"""
    
    @staticmethod
    def generate_analytics(df: Optional[pd.DataFrame]) -> Dict[str, Any]:
        """Generate comprehensive analytics from DataFrame"""
        if df is None or df.empty:
            return {
                'error': 'No data provided',
                'total_events': 0,
                'columns': [],
                'summary': 'No data to analyze'
            }
        
        try:
            analytics = {
                'total_events': len(df),
                'total_columns': len(df.columns),
                'columns': list(df.columns),
                'data_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'sample_data': df.head(5).to_dict('records'),
                'missing_data': df.isnull().sum().to_dict(),
                'data_quality': {
                    'total_missing_values': df.isnull().sum().sum(),
                    'completeness_percentage': ((df.size - df.isnull().sum().sum()) / df.size * 100) if df.size > 0 else 0
                }
            }
            
            # Add numeric summaries
            numeric_columns = df.select_dtypes(include=['number']).columns
            if len(numeric_columns) > 0:
                analytics['numeric_summary'] = {}
                for col in numeric_columns:
                    analytics['numeric_summary'][col] = {
                        'mean': float(df[col].mean()) if not df[col].isnull().all() else 0,
                        'median': float(df[col].median()) if not df[col].isnull().all() else 0,
                        'min': float(df[col].min()) if not df[col].isnull().all() else 0,
                        'max': float(df[col].max()) if not df[col].isnull().all() else 0
                    }
            
            # Add categorical summaries
            categorical_columns = df.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                analytics['categorical_summary'] = {}
                for col in categorical_columns:
                    value_counts = df[col].value_counts().head(10)
                    analytics['categorical_summary'][col] = value_counts.to_dict()
            
            return analytics
            
        except Exception as e:
            return {
                'error': f'Analytics generation failed: {str(e)}',
                'total_events': len(df) if df is not None else 0,
                'columns': list(df.columns) if df is not None else []
            }

# For backward compatibility
__all__ = ['AnalyticsGenerator']
