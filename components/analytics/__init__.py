# components/analytics/__init__.py - FIXED: Safe analytics imports
"""
Analytics components module - Type-safe imports
"""

# Import main component functions with error handling
try:
    from plugins.file_upload_plugin import create_file_uploader, FileProcessor
except ImportError as e:
    print(f"Warning: Could not import file_upload_plugin: {e}")

    def create_file_uploader(*args, **kwargs):
        """Fallback basic file uploader"""
        from dash import html, dcc

        upload_id = kwargs.get("upload_id", "basic-file-upload")

        return html.Div(
            [
                dcc.Upload(
                    id=upload_id,
                    children=html.Div("Drag and drop or click to upload"),
                    multiple=True,
                    style={
                        "border": "1px dashed #ccc",
                        "padding": "2rem",
                        "textAlign": "center",
                    },
                ),
                html.Div(id=f"{upload_id}-status"),
                html.Div(id=f"{upload_id}-info"),
                dcc.Store(
                    id=f"{upload_id}-state", data={"status": "idle", "files": []}
                ),
            ]
        )

    FileProcessor = None

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


# Handle file processing imports if not provided by the plugin
AnalyticsGenerator = None

try:
    from .file_processing import (
        FileProcessor as _FP,
        AnalyticsGenerator as _AnalyticsGenerator,
    )

    if "FileProcessor" not in globals() or FileProcessor is None:
        FileProcessor = _FP
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
    "create_file_uploader",
    "create_data_preview",
    "create_analytics_charts",
    "create_summary_cards",
    "FileProcessor",
    "AnalyticsGenerator",
]
