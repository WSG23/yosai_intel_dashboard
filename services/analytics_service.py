# services/analytics_service.py - FIXED: Modular analytics service
"""
Analytics Service for Yōsai Intel Dashboard
Centralized business logic for all analytics operations
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass

# Import modular components
from models.access_events import AccessEventModel, create_access_event_model
from models.enums import AccessResult, AnomalyType, SeverityLevel
from config.database_manager import get_database

@dataclass
class AnalyticsConfig:
    """Configuration for analytics operations"""
    default_time_range_days: int = 30
    max_records_per_query: int = 10000
    cache_timeout_seconds: int = 300
    min_confidence_threshold: float = 0.7

class AnalyticsService:
    """Centralized analytics service for all dashboard operations"""
    
    def __init__(self, config: Optional[AnalyticsConfig] = None):
        self.config = config or AnalyticsConfig()
        self.db = get_database()
        self.access_model = create_access_event_model(self.db)
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
    
    def _get_cached_or_execute(self, cache_key: str, execute_func) -> Any:
        """Get cached result or execute function and cache result"""
        current_time = datetime.now()
        
        # Check if cached and not expired
        if (cache_key in self._cache and 
            cache_key in self._cache_timestamps and
            (current_time - self._cache_timestamps[cache_key]).seconds < self.config.cache_timeout_seconds):
            return self._cache[cache_key]
        
        # Execute and cache
        try:
            result = execute_func()
            self._cache[cache_key] = result
            self._cache_timestamps[cache_key] = current_time
            return result
        except Exception as e:
            logging.error(f"Error executing cached function {cache_key}: {e}")
            return None
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        
        def _calculate_summary():
            summary_stats = self.access_model.get_summary_stats()
            recent_events = self.access_model.get_recent_events(hours=24)
            
            return {
                'total_events_30d': summary_stats.get('total_events', 0),
                'unique_users_30d': summary_stats.get('unique_people', 0),
                'unique_doors_30d': summary_stats.get('unique_doors', 0),
                'granted_rate': summary_stats.get('granted_rate', 0),
                'denied_rate': summary_stats.get('denied_rate', 0),
                'recent_events_24h': len(recent_events),
                'last_updated': datetime.now().isoformat(),
                'system_status': self._calculate_system_status(summary_stats)
            }
        
        return self._get_cached_or_execute('dashboard_summary', _calculate_summary)
    
    def _calculate_system_status(self, stats: Dict[str, Any]) -> str:
        """Calculate overall system status based on metrics"""
        denied_rate = stats.get('denied_rate', 0)
        total_events = stats.get('total_events', 0)
        
        if total_events == 0:
            return 'no_data'
        elif denied_rate < 5:
            return 'healthy'
        elif denied_rate < 15:
            return 'warning'
        else:
            return 'critical'
    
    def get_access_patterns_analysis(self, days: int = 30) -> Dict[str, Any]:
        """Analyze access patterns over specified period"""
        
        def _analyze_patterns():
            # Get trend data
            trends = self.access_model.get_trend_analysis(days)
            hourly_dist = self.access_model.get_hourly_distribution(days)
            user_activity = self.access_model.get_user_activity(limit=10)
            door_activity = self.access_model.get_door_activity(limit=10)
            
            return {
                'daily_trends': self._process_trends(trends),
                'hourly_distribution': self._process_hourly_distribution(hourly_dist),
                'top_users': self._process_user_activity(user_activity),
                'top_doors': self._process_door_activity(door_activity),
                'anomaly_indicators': self._detect_pattern_anomalies(trends, hourly_dist)
            }
        
        cache_key = f'access_patterns_{days}d'
        return self._get_cached_or_execute(cache_key, _analyze_patterns)
    
    def _process_trends(self, trends_df: pd.DataFrame) -> Dict[str, Any]:
        """Process daily trends data for visualization"""
        if trends_df.empty:
            return {}
        
        try:
            return {
                'dates': trends_df['date'].tolist(),
                'total_events': trends_df['total_events'].tolist(),
                'granted_events': trends_df['granted_events'].tolist(),
                'denied_events': trends_df['denied_events'].tolist(),
                'success_rates': trends_df['success_rate'].tolist(),
                'unique_users': trends_df['unique_users'].tolist()
            }
        except Exception as e:
            logging.error(f"Error processing trends: {e}")
            return {}
    
    def _process_hourly_distribution(self, hourly_df: pd.DataFrame) -> Dict[str, Any]:
        """Process hourly distribution for pattern analysis"""
        if hourly_df.empty:
            return {}
        
        try:
            # Fill missing hours with zeros
            all_hours = pd.DataFrame({'hour': [f'{i:02d}' for i in range(24)]})
            merged = all_hours.merge(hourly_df, on='hour', how='left').fillna(0)
            
            return {
                'hours': merged['hour'].tolist(),
                'event_counts': merged['event_count'].astype(int).tolist(),
                'granted_counts': merged['granted_count'].astype(int).tolist(),
                'peak_hours': self._identify_peak_hours(merged),
                'off_hours_activity': self._identify_off_hours_activity(merged)
            }
        except Exception as e:
            logging.error(f"Error processing hourly distribution: {e}")
            return {}
    
    def _identify_peak_hours(self, hourly_data: pd.DataFrame) -> List[str]:
        """Identify peak activity hours"""
        try:
            threshold = hourly_data['event_count'].quantile(0.8)
            peak_hours = hourly_data[hourly_data['event_count'] >= threshold]['hour'].tolist()
            return peak_hours
        except Exception:
            return []
    
    def _identify_off_hours_activity(self, hourly_data: pd.DataFrame) -> Dict[str, Any]:
        """Identify unusual off-hours activity"""
        try:
            # Define off-hours (10 PM to 6 AM)
            off_hours = [f'{i:02d}' for i in list(range(22, 24)) + list(range(0, 6))]
            off_hours_data = hourly_data[hourly_data['hour'].isin(off_hours)]
            
            total_off_hours = off_hours_data['event_count'].sum()
            total_events = hourly_data['event_count'].sum()
            
            off_hours_percentage = (total_off_hours / total_events * 100) if total_events > 0 else 0
            
            return {
                'total_off_hours_events': int(total_off_hours),
                'percentage_of_total': round(off_hours_percentage, 2),
                'is_anomalous': off_hours_percentage > 20  # More than 20% is unusual
            }
        except Exception as e:
            logging.error(f"Error analyzing off-hours activity: {e}")
            return {}
    
    def _process_user_activity(self, user_df: pd.DataFrame) -> Dict[str, Any]:
        """Process user activity data"""
        if user_df.empty:
            return {}
        
        try:
            return {
                'user_ids': user_df['person_id'].tolist(),
                'total_events': user_df['total_events'].tolist(),
                'granted_events': user_df['granted_events'].tolist(),
                'success_rates': (user_df['granted_events'] / user_df['total_events'] * 100).round(2).tolist(),
                'last_access': user_df['last_access'].tolist()
            }
        except Exception as e:
            logging.error(f"Error processing user activity: {e}")
            return {}
    
    def _process_door_activity(self, door_df: pd.DataFrame) -> Dict[str, Any]:
        """Process door activity data"""
        if door_df.empty:
            return {}
        
        try:
            return {
                'door_ids': door_df['door_id'].tolist(),
                'total_events': door_df['total_events'].tolist(),
                'granted_events': door_df['granted_events'].tolist(),
                'unique_users': door_df['unique_users'].tolist(),
                'success_rates': (door_df['granted_events'] / door_df['total_events'] * 100).round(2).tolist()
            }
        except Exception as e:
            logging.error(f"Error processing door activity: {e}")
            return {}
    
    def _detect_pattern_anomalies(self, trends_df: pd.DataFrame, hourly_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in access patterns"""
        anomalies = []
        
        try:
            # Check for sudden spikes in denied access
            if not trends_df.empty:
                recent_denied_rate = trends_df['denied_events'].tail(7).mean()
                historical_denied_rate = trends_df['denied_events'].head(-7).mean() if len(trends_df) > 7 else 0
                
                if recent_denied_rate > historical_denied_rate * 1.5:
                    anomalies.append({
                        'type': 'denied_access_spike',
                        'severity': 'medium',
                        'description': f'Recent denied access rate increased by {((recent_denied_rate/historical_denied_rate - 1) * 100):.1f}%'
                    })
            
            # Check for unusual off-hours activity
            off_hours_data = self._identify_off_hours_activity(hourly_df)
            if off_hours_data.get('is_anomalous', False):
                anomalies.append({
                    'type': 'off_hours_activity',
                    'severity': 'low',
                    'description': f'{off_hours_data["percentage_of_total"]:.1f}% of activity during off-hours'
                })
            
        except Exception as e:
            logging.error(f"Error detecting anomalies: {e}")
        
        return anomalies
    
    def process_uploaded_file(self, df: pd.DataFrame, filename: str) -> Dict[str, Any]:
        """Process uploaded file and generate analytics"""
        
        try:
            # Validate the data
            if not self.access_model.validate_data(df):
                return {
                    'success': False,
                    'error': 'Data validation failed',
                    'filename': filename
                }
            
            # Generate analytics
            analytics = self._generate_file_analytics(df)
            
            return {
                'success': True,
                'filename': filename,
                'row_count': len(df),
                'column_count': len(df.columns),
                'analytics': analytics,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error processing uploaded file {filename}: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }
    
    def _generate_file_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate analytics from uploaded DataFrame"""
        
        analytics = {
            'total_events': len(df),
            'date_range': self._extract_date_range(df),
            'access_patterns': self._extract_access_patterns(df),
            'hourly_patterns': self._extract_hourly_patterns(df),
            'user_activity': self._extract_user_activity(df),
            'door_activity': self._extract_door_activity(df)
        }
        
        return analytics
    
    def _extract_date_range(self, df: pd.DataFrame) -> Dict[str, Optional[str]]:
        """Extract date range from DataFrame"""
        try:
            date_columns = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
            if date_columns:
                date_col = date_columns[0]
                dates = pd.to_datetime(df[date_col], errors='coerce').dropna()
                if not dates.empty:
                    return {
                        'start': dates.min().strftime('%Y-%m-%d'),
                        'end': dates.max().strftime('%Y-%m-%d')
                    }
        except Exception as e:
            logging.error(f"Error extracting date range: {e}")
        
        return {'start': None, 'end': None}
    
    def _extract_access_patterns(self, df: pd.DataFrame) -> Dict[str, int]:
        """Extract access result patterns"""
        try:
            access_columns = [col for col in df.columns if 'access' in col.lower() or 'result' in col.lower()]
            if access_columns:
                access_col = access_columns[0]
                return df[access_col].value_counts().to_dict()
        except Exception as e:
            logging.error(f"Error extracting access patterns: {e}")
        
        return {}
    
    def _extract_hourly_patterns(self, df: pd.DataFrame) -> Dict[str, int]:
        """Extract hourly access patterns"""
        try:
            date_columns = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
            if date_columns:
                date_col = date_columns[0]
                df_copy = df.copy()
                df_copy['hour'] = pd.to_datetime(df_copy[date_col], errors='coerce').dt.hour
                return df_copy['hour'].value_counts().sort_index().to_dict()
        except Exception as e:
            logging.error(f"Error extracting hourly patterns: {e}")
        
        return {}
    
    def _extract_user_activity(self, df: pd.DataFrame) -> Dict[str, int]:
        """Extract user activity patterns"""
        try:
            user_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['user', 'person', 'employee'])]
            if user_columns:
                user_col = user_columns[0]
                return df[user_col].value_counts().head(10).to_dict()
        except Exception as e:
            logging.error(f"Error extracting user activity: {e}")
        
        return {}
    
    def _extract_door_activity(self, df: pd.DataFrame) -> Dict[str, int]:
        """Extract door activity patterns"""
        try:
            door_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['door', 'location', 'device'])]
            if door_columns:
                door_col = door_columns[0]
                return df[door_col].value_counts().head(10).to_dict()
        except Exception as e:
            logging.error(f"Error extracting door activity: {e}")
        
        return {}
    
    def clear_cache(self) -> None:
        """Clear the analytics cache"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logging.info("Analytics cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'cached_items': len(self._cache),
            'oldest_cache': min(self._cache_timestamps.values()) if self._cache_timestamps else None,
            'newest_cache': max(self._cache_timestamps.values()) if self._cache_timestamps else None
        }

# Factory function for dependency injection
def create_analytics_service(config: Optional[AnalyticsConfig] = None) -> AnalyticsService:
    """Factory function to create AnalyticsService instance"""
    return AnalyticsService(config)

# Export the service class and factory
__all__ = ['AnalyticsService', 'AnalyticsConfig', 'create_analytics_service']
