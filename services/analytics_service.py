"""
Modular analytics service implementation
"""
import pandas as pd
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass

from services.protocols import AnalyticsProtocol
from services.base import ServiceResult


@dataclass
class AnalyticsConfig:
    """Configuration options for :class:`AnalyticsService`."""

    cache_timeout_seconds: int = 300
    default_time_range_days: int = 7

logger = logging.getLogger(__name__)

class AnalyticsService(AnalyticsProtocol):
    """Analytics service with protocol compliance"""

    def __init__(
        self,
        config: Optional[AnalyticsConfig] = None,
        database_connection: Optional[Any] = None,
    ) -> None:
        self.database = database_connection
        self.config = config or AnalyticsConfig()
        self.logger = logging.getLogger(__name__)
        self._cache: Dict[str, Tuple[datetime, Any]] = {}

    def _get_cached_or_execute(self, key: str, func: Callable[[], Any]) -> Any:
        """Return cached value if within timeout, otherwise execute function."""
        cached = self._cache.get(key)
        if cached:
            ts, value = cached
            if (datetime.now() - ts).total_seconds() < self.config.cache_timeout_seconds:
                return value
        result = func()
        self._cache[key] = (datetime.now(), result)
        return result

    def analyze_data(self, data: pd.DataFrame) -> ServiceResult:
        """High-level data analysis entry point."""
        result = self.analyze_access_patterns(data)
        if not result.success:
            return result

        analysis = result.data or {}
        summary = {
            'total_records': analysis.get('total_events', len(data)),
            'unique_users': analysis.get('unique_users', 0),
        }
        return ServiceResult(True, data=summary)
    
    def analyze_access_patterns(self, data: pd.DataFrame) -> ServiceResult:
        """Analyze access patterns in DataFrame"""
        try:
            if data.empty:
                return ServiceResult(False, error='No data provided for analysis')

            analysis = {
                'total_events': len(data),
                'processed_at': datetime.now().isoformat(),
                'columns_found': list(data.columns)
            }
            
            # Access result analysis
            if 'access_result' in data.columns:
                access_counts = data['access_result'].value_counts()
                analysis['access_patterns'] = access_counts.to_dict()
            
            # User activity analysis
            if 'person_id' in data.columns:
                user_counts = data['person_id'].value_counts().head(10)
                analysis['top_users'] = user_counts.to_dict()
                analysis['unique_users'] = data['person_id'].nunique()
            
            # Door activity analysis
            if 'door_id' in data.columns:
                door_counts = data['door_id'].value_counts().head(10)
                analysis['top_doors'] = door_counts.to_dict()
                analysis['unique_doors'] = data['door_id'].nunique()
            
            # Time-based analysis
            if 'timestamp' in data.columns:
                try:
                    data['timestamp'] = pd.to_datetime(data['timestamp'])
                    data['hour'] = data['timestamp'].dt.hour
                    hourly_counts = data['hour'].value_counts().sort_index()
                    analysis['hourly_patterns'] = hourly_counts.to_dict()
                except Exception as e:
                    self.logger.warning(f"Time analysis failed: {e}")
            
            return ServiceResult(True, data=analysis)

        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return ServiceResult(False, error=f'Analysis failed: {str(e)}')
    
    def detect_anomalies(self, events: List[Dict[str, Any]]) -> ServiceResult:
        """Detect anomalies in access events"""
        try:
            if not events:
                return ServiceResult(True, data=[])
            
            anomalies = []
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(events)
            
            # Detect unusual access times
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['hour'] = df['timestamp'].dt.hour
                
                # Flag events outside normal hours (9 AM - 6 PM)
                unusual_hours = df[(df['hour'] < 9) | (df['hour'] > 18)]
                for _, event in unusual_hours.iterrows():
                    anomalies.append({
                        'type': 'unusual_time',
                        'event_id': event.get('event_id', 'unknown'),
                        'hour': int(event['hour']),
                        'description': f'Access at unusual hour: {event["hour"]}:00'
                    })
            
            # Detect multiple failed attempts
            if 'access_result' in df.columns and 'person_id' in df.columns:
                failed_attempts = df[df['access_result'] == 'Denied']
                user_failures = failed_attempts.groupby('person_id').size()
                high_failure_users = user_failures[user_failures > 3]
                
                for user_id, failure_count in high_failure_users.items():
                    anomalies.append({
                        'type': 'multiple_failures',
                        'person_id': user_id,
                        'failure_count': int(failure_count),
                        'description': f'User {user_id} has {failure_count} failed attempts'
                    })
            
            return ServiceResult(True, data=anomalies)

        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return ServiceResult(False, error=f'Anomaly detection failed: {e}')

# Factory function for easy instantiation
def create_analytics_service(
    config: Optional[AnalyticsConfig] = None,
    database_connection: Optional[Any] = None,
) -> AnalyticsService:
    """Create analytics service instance"""
    return AnalyticsService(config, database_connection)

# Module exports
__all__ = ['AnalyticsService', 'AnalyticsConfig', 'create_analytics_service']
