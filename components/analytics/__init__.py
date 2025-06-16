# components/analytics/__init__.py - FIXED: Safe analytics imports
"""
Analytics components module - Type-safe imports
"""

# Import main component functions with error handling
try:
    from .file_uploader import create_file_uploader
except ImportError as e:
    print(f"Warning: Could not import file_uploader: {e}")
    def create_file_uploader(*args, **kwargs):
        from dash import html
        return html.Div("File uploader component not available")

try:
    from .data_preview import create_data_preview
except ImportError as e:
    print(f"Warning: Could not import data_preview: {e}")
    def create_data_preview(*args, **kwargs):
        from dash import html
        return html.Div("Data preview component not available")

try:
    from .analytics_charts import create_analytics_charts, create_summary_cards
except ImportError as e:
    print(f"Warning: Could not import analytics_charts: {e}")
    def create_analytics_charts(*args, **kwargs):
        from dash import html
        return html.Div("Analytics charts component not available")
    
    def create_summary_cards(*args, **kwargs):
        from dash import html
        return html.Div("Summary cards component not available")

# Handle file processing imports
FileProcessor = None
AnalyticsGenerator = None

try:
    from .file_processing import FileProcessor as _FileProcessor, AnalyticsGenerator as _AnalyticsGenerator
    FileProcessor = _FileProcessor
    AnalyticsGenerator = _AnalyticsGenerator
except ImportError as e:
    print(f"Warning: Could not import file_processing: {e}")
    
    # Create fallback classes
    class _FallbackFileProcessor:
        @staticmethod
        def process_file_content(contents, filename):
            return None
        
        @staticmethod
        def validate_dataframe(df):
            return True, "Fallback validation", []
    
    class _FallbackAnalyticsGenerator:
        @staticmethod
        def generate_analytics(df):
            return {}
    
    FileProcessor = _FallbackFileProcessor
    AnalyticsGenerator = _FallbackAnalyticsGenerator

# Export all public functions
__all__ = [
    'create_file_uploader',
    'create_data_preview', 
    'create_analytics_charts',
    'create_summary_cards',
    'FileProcessor',
    'AnalyticsGenerator'
]
