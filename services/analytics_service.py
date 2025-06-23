"""
Analytics service implementation
"""
import pandas as pd
from typing import Dict, Any, List
from .base import AnalyticsServiceProtocol, ServiceResult
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Production analytics service implementation"""

    def analyze_data(self, data: pd.DataFrame) -> ServiceResult:
        """Analyze DataFrame and return insights"""
        try:
            if data.empty:
                return ServiceResult(success=False, error="No data provided for analysis")

            analytics: Dict[str, Any] = {
                'total_records': len(data),
                'columns': list(data.columns),
                'data_types': data.dtypes.to_dict(),
                'missing_values': data.isnull().sum().to_dict(),
                'processed_at': pd.Timestamp.now().isoformat()
            }

            if 'access_result' in data.columns:
                analytics['access_patterns'] = data['access_result'].value_counts().to_dict()
            if 'person_id' in data.columns:
                analytics['unique_users'] = data['person_id'].nunique()
            if 'door_id' in data.columns:
                analytics['unique_doors'] = data['door_id'].nunique()

            return ServiceResult(success=True, data=analytics)
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return ServiceResult(success=False, error=f"Analysis failed: {str(e)}")

    def detect_anomalies(self, data: pd.DataFrame) -> ServiceResult:
        """Simple anomaly detection"""
        try:
            anomalies: List[Dict[str, Any]] = []
            warnings: List[str] = []

            if 'timestamp' in data.columns:
                if not pd.api.types.is_datetime64_any_dtype(data['timestamp']):
                    data['timestamp'] = pd.to_datetime(data['timestamp'], errors='coerce')
                data['hour'] = data['timestamp'].dt.hour
                hour_counts = data['hour'].value_counts()
                low_activity_hours = hour_counts[hour_counts < hour_counts.mean() * 0.1]
                if not low_activity_hours.empty:
                    anomalies.append({
                        'type': 'low_activity_hours',
                        'hours': low_activity_hours.index.tolist(),
                        'description': 'Hours with unusually low activity'
                    })

            return ServiceResult(success=True, data={'anomalies': anomalies}, warnings=warnings)
        except Exception as e:
            logger.error(f"Anomaly detection error: {e}")
            return ServiceResult(success=False, error=f"Anomaly detection failed: {str(e)}")
