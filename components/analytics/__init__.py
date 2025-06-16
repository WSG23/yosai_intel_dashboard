# components/analytics/__init__.py - Fixed imports for modular structure
"""
Analytics components module for Yōsai Intel Dashboard
Modular, testable components for data analysis and visualization
"""

# Import main component functions
from .file_uploader import create_file_uploader
from .data_preview import create_data_preview
from .analytics_charts import create_analytics_charts, create_summary_cards
from .file_processing import FileProcessor, AnalyticsGenerator

# Export all public functions
__all__ = [
    'create_file_uploader',
    'create_data_preview', 
    'create_analytics_charts',
    'create_summary_cards',
    'FileProcessor',
    'AnalyticsGenerator'
]

# Version information
__version__ = "1.0.0"
__author__ = "Yōsai Intel Team"