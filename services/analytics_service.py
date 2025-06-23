"""
Modular analytics service implementation
"""
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from services.protocols import AnalyticsProtocol

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Analytics service with protocol compliance"""
    
    def __init__(self, database_connection: Optional[Any] = None):
        self.database = database_connection
        self.logger = logging.getLogger(__name__)
    
    def analyze_access_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze access patterns in DataFrame"""
        try:
            if data.empty:
                return {'error': 'No data provided for analysis'}
            
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
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            return {'error': f'Analysis failed: {str(e)}'}
    
    def detect_anomalies(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in access events"""
        try:
            if not events:
                return []
            
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
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []

# Factory function for easy instantiation
def create_analytics_service(database_connection: Optional[Any] = None) -> AnalyticsService:
    """Create analytics service instance"""
    return AnalyticsService(database_connection)

# Module exports
__all__ = ['AnalyticsService', 'create_analytics_service']
