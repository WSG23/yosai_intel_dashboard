"""
Analytics Service for Yōsai Intel Dashboard
Handles data analysis, statistics, and anomaly detection
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from .base import BaseService
from .protocols import DatabaseProtocol, AnalyticsProtocol

logger = logging.getLogger(__name__)

class AnalyticsService(BaseService):
    """Analytics service implementation"""
    
    def __init__(self, database: Optional[DatabaseProtocol] = None):
        super().__init__("analytics_service")
        self.database = database
    
    def _do_initialize(self) -> None:
        """Initialize analytics service"""
        if self.database:
            # Test database connection
            health = self.database.health_check()
            if health.get('status') != 'healthy':
                raise RuntimeError(f"Database unhealthy: {health}")
    
    def get_summary_stats(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics for access events"""
        if data.empty:
            return {
                'total_events': 0,
                'unique_persons': 0,
                'unique_doors': 0,
                'time_range': None,
                'access_success_rate': 0.0
            }
        
        stats = {
            'total_events': len(data),
            'unique_persons': data['person_id'].nunique() if 'person_id' in data.columns else 0,
            'unique_doors': data['door_id'].nunique() if 'door_id' in data.columns else 0,
            'time_range': {
                'start': data['timestamp'].min() if 'timestamp' in data.columns else None,
                'end': data['timestamp'].max() if 'timestamp' in data.columns else None
            }
        }
        
        # Calculate success rate
        if 'access_result' in data.columns:
            total_attempts = len(data)
            successful = len(data[data['access_result'].isin(['Granted', 'granted', 'GRANTED'])])
            stats['access_success_rate'] = successful / total_attempts if total_attempts > 0 else 0.0
        else:
            stats['access_success_rate'] = 0.0
        
        return stats
    
    def detect_anomalies(self, data: pd.DataFrame) -> pd.DataFrame:
        """Simple anomaly detection"""
        if data.empty or 'timestamp' not in data.columns:
            return pd.DataFrame()
        
        # Simple time-based anomaly detection
        data = data.copy()
        data['hour'] = pd.to_datetime(data['timestamp']).dt.hour
        
        # Flag access outside business hours (assuming 9-17)
        data['is_anomaly'] = (data['hour'] < 9) | (data['hour'] > 17)
        data['anomaly_reason'] = data['is_anomaly'].apply(
            lambda x: 'Outside business hours' if x else None
        )
        
        return data[data['is_anomaly']]
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for analytics service"""
        health = super().health_check()
        
        if self.database:
            db_health = self.database.health_check()
            health['database'] = db_health
        
        return health

def create_analytics_service(config=None, database=None) -> AnalyticsService:
    """Factory function to create analytics service"""
    service = AnalyticsService(database)
    service.initialize()
    return service
