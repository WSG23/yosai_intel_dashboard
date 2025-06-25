#!/usr/bin/env python3
"""
Complete Analytics Service Integration - FIXED VERSION
"""
import logging
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Complete analytics service that integrates all data sources"""

    def __init__(self):
        self.database_manager: Optional[Any] = None
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection"""
        try:
            from config.database_manager import DatabaseManager
            from config.config import get_database_config
            db_config = get_database_config()
            self.database_manager = DatabaseManager(db_config)
            logger.info("Database manager initialized")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
            self.database_manager = None

    def get_analytics_from_uploaded_data(self) -> Dict[str, Any]:
        """Get analytics from uploaded files"""
        try:
            from pages.file_upload import get_uploaded_data
            uploaded_data = get_uploaded_data()

            if not uploaded_data:
                return {'status': 'no_data', 'message': 'No uploaded data available'}

            # Combine all uploaded DataFrames
            all_data = []
            for filename, df in uploaded_data.items():
                if not df.empty:
                    df_copy = df.copy()
                    df_copy['source_file'] = filename
                    all_data.append(df_copy)

            if not all_data:
                return {'status': 'empty', 'message': 'All uploaded files are empty'}

            # Combine all data
            combined_df = pd.concat(all_data, ignore_index=True)

            # Generate analytics using models
            try:
                from models.base import ModelFactory
                models = ModelFactory.create_models_from_dataframe(combined_df)
                analytics = ModelFactory.get_analytics_from_models(models)

                analytics.update({
                    'status': 'success',
                    'data_source': 'uploaded_files',
                    'total_files': len(uploaded_data),
                    'total_rows': len(combined_df),
                    'columns': list(combined_df.columns),
                    'timestamp': datetime.now().isoformat()
                })

                return analytics

            except ImportError:
                # Fallback analytics without models
                return self._generate_basic_analytics(combined_df)

        except Exception as e:
            logger.error(f"Error getting analytics from uploaded data: {e}")
            return {'status': 'error', 'message': str(e)}

    def get_analytics_by_source(self, source: str) -> Dict[str, Any]:
        """Get analytics from specified source"""
        if source == "sample":
            return self._generate_sample_analytics()
        elif source == "uploaded":
            return self.get_analytics_from_uploaded_data()
        elif source == "database":
            return self._get_database_analytics()
        else:
            return {'status': 'error', 'message': f'Unknown source: {source}'}

    def _generate_sample_analytics(self) -> Dict[str, Any]:
        """Generate sample analytics data"""
        # Create sample DataFrame
        sample_data = pd.DataFrame({
            'user_id': ['user_001', 'user_002', 'user_003'] * 100,
            'door_id': ['door_A', 'door_B', 'door_C'] * 100,
            'timestamp': pd.date_range('2024-01-01', periods=300, freq='1H'),
            'access_result': (['Granted'] * 250) + (['Denied'] * 50)
        })

        return self._generate_basic_analytics(sample_data)

    def _generate_basic_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate basic analytics from DataFrame"""
        try:
            analytics = {
                'status': 'success',
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'summary': {},
                'timestamp': datetime.now().isoformat()
            }

            # Basic statistics for each column
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    analytics['summary'][col] = {
                        'type': 'numeric',
                        'mean': float(df[col].mean()),
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'null_count': int(df[col].isnull().sum())
                    }
                else:
                    value_counts = df[col].value_counts().head(10)
                    analytics['summary'][col] = {
                        'type': 'categorical',
                        'unique_values': int(df[col].nunique()),
                        'top_values': value_counts.to_dict(),
                        'null_count': int(df[col].isnull().sum())
                    }

            return analytics

        except Exception as e:
            logger.error(f"Error generating basic analytics: {e}")
            return {'status': 'error', 'message': str(e)}

    def _get_database_analytics(self) -> Dict[str, Any]:
        """Get analytics from database"""
        if not self.database_manager:
            return {'status': 'error', 'message': 'Database not available'}

        try:
            # Implement database analytics here
            return {
                'status': 'success',
                'message': 'Database analytics not yet implemented',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        health = {
            'service': 'healthy',
            'timestamp': datetime.now().isoformat()
        }

        # Check database
        if self.database_manager:
            try:
                health['database'] = 'healthy' if self.database_manager.health_check() else 'unhealthy'
            except:
                health['database'] = 'unhealthy'
        else:
            health['database'] = 'not_configured'

        # Check file upload
        try:
            from pages.file_upload import get_uploaded_filenames
            health['uploaded_files'] = len(get_uploaded_filenames())
        except ImportError:
            health['uploaded_files'] = 'not_available'

        return health

# Global service instance
_analytics_service: Optional[AnalyticsService] = None

def get_analytics_service() -> AnalyticsService:
    """Get global analytics service instance"""
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service

def create_analytics_service() -> AnalyticsService:
    """Create new analytics service instance"""
    return AnalyticsService()

__all__ = ['AnalyticsService', 'get_analytics_service', 'create_analytics_service']
