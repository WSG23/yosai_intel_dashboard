"""Analytics components - Direct imports"""

# Direct exports
try:
    from .file_uploader import create_dual_file_uploader
    from .data_preview import create_data_preview
    from .analytics_charts import create_analytics_charts, create_summary_cards
    UPLOAD_AVAILABLE = True
except Exception as e:
    print(f"Upload components not available: {e}")
    create_dual_file_uploader = None
    create_data_preview = None
    create_analytics_charts = None
    create_summary_cards = None
    UPLOAD_AVAILABLE = False

# Try to import optional components
try:
    from .file_processing import FileProcessor, AnalyticsGenerator
except ImportError:
    FileProcessor = None
    AnalyticsGenerator = None

__all__ = [
    'create_dual_file_uploader',
    'create_data_preview',
    'create_analytics_charts',
    'create_summary_cards',
    'FileProcessor',
    'AnalyticsGenerator',
    'UPLOAD_AVAILABLE'
]
