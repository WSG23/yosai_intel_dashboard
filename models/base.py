#!/usr/bin/env python3
"""
Complete Models Base System - Missing piece for consolidation
"""
import logging
import pandas as pd
from typing import Dict, Any, List, Optional, Protocol
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseModel:
    """Base class for all models"""

    def __init__(self, data_source: Optional[Any] = None):
        self.data_source = data_source
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            'created_at': self.created_at.isoformat(),
            'data_source': str(self.data_source) if self.data_source else None
        }

    def validate(self) -> bool:
        """Validate model data"""
        return True


class AccessEventModel(BaseModel):
    """Model for access control events"""

    def __init__(self, data_source: Optional[Any] = None):
        super().__init__(data_source)
        self.events: List[Dict[str, Any]] = []

    def load_from_dataframe(self, df: pd.DataFrame) -> bool:
        """Load events from pandas DataFrame"""
        try:
            if df is None or df.empty:
                logger.warning("Empty DataFrame provided to AccessEventModel")
                return False

            # Convert DataFrame to list of dictionaries
            self.events = df.to_dict('records')
            logger.info(f"Loaded {len(self.events)} access events")
            return True

        except Exception as e:
            logger.error(f"Error loading DataFrame into AccessEventModel: {e}")
            return False

    def get_user_activity(self) -> Dict[str, int]:
        """Get user activity summary"""
        if not self.events:
            return {}

        try:
            # Count events per user
            user_counts = {}
            for event in self.events:
                user_id = event.get('user_id') or event.get('person_id') or 'unknown'
                user_counts[user_id] = user_counts.get(user_id, 0) + 1

            return user_counts
        except Exception as e:
            logger.error(f"Error calculating user activity: {e}")
            return {}

    def get_door_activity(self) -> Dict[str, int]:
        """Get door activity summary"""
        if not self.events:
            return {}

        try:
            # Count events per door
            door_counts = {}
            for event in self.events:
                door_id = event.get('door_id') or event.get('location') or 'unknown'
                door_counts[door_id] = door_counts.get(door_id, 0) + 1

            return door_counts
        except Exception as e:
            logger.error(f"Error calculating door activity: {e}")
            return {}

    def get_access_patterns(self) -> Dict[str, int]:
        """Get access pattern summary"""
        if not self.events:
            return {}

        try:
            patterns = {}
            for event in self.events:
                result = event.get('access_result') or event.get('status') or 'unknown'
                patterns[result] = patterns.get(result, 0) + 1

            return patterns
        except Exception as e:
            logger.error(f"Error calculating access patterns: {e}")
            return {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with analytics"""
        base_dict = super().to_dict()
        base_dict.update({
            'total_events': len(self.events),
            'user_activity': self.get_user_activity(),
            'door_activity': self.get_door_activity(),
            'access_patterns': self.get_access_patterns()
        })
        return base_dict


class AnomalyDetectionModel(BaseModel):
    """Model for anomaly detection"""

    def __init__(self, data_source: Optional[Any] = None):
        super().__init__(data_source)
        self.anomalies: List[Dict[str, Any]] = []

    def detect_anomalies(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Simple anomaly detection"""
        anomalies = []

        try:
            # Simple anomaly detection rules
            for event in events:
                # After hours access (assuming 6 PM to 6 AM is after hours)
                timestamp = event.get('timestamp', '')
                if isinstance(timestamp, str) and ('20:' in timestamp or '21:' in timestamp or \
                                                   '22:' in timestamp or '23:' in timestamp or
                                                   '00:' in timestamp or '01:' in timestamp or
                                                   '02:' in timestamp or '03:' in timestamp or
                                                   '04:' in timestamp or '05:' in timestamp):
                    anomalies.append({
                        'type': 'after_hours_access',
                        'event': event,
                        'description': 'Access attempt after business hours'
                    })

                # Failed access attempts
                result = event.get('access_result', event.get('status', '')).lower()
                if 'denied' in result or 'failed' in result or 'fail' in result:
                    anomalies.append({
                        'type': 'failed_access',
                        'event': event,
                        'description': 'Failed access attempt'
                    })

            self.anomalies = anomalies
            return anomalies

        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []


class ModelFactory:
    """Factory for creating model instances"""

    @staticmethod
    def create_access_model(data_source: Optional[Any] = None) -> AccessEventModel:
        """Create AccessEventModel instance"""
        return AccessEventModel(data_source)

    @staticmethod
    def create_anomaly_model(data_source: Optional[Any] = None) -> AnomalyDetectionModel:
        """Create AnomalyDetectionModel instance"""
        return AnomalyDetectionModel(data_source)

    @staticmethod
    def create_models_from_dataframe(df: pd.DataFrame) -> Dict[str, BaseModel]:
        """Create all models from a DataFrame"""
        models = {}

        try:
            # Create access model
            access_model = ModelFactory.create_access_model(df)
            if access_model.load_from_dataframe(df):
                models['access'] = access_model

            # Create anomaly model
            anomaly_model = ModelFactory.create_anomaly_model(df)
            events = df.to_dict('records') if not df.empty else []
            anomaly_model.detect_anomalies(events)
            models['anomaly'] = anomaly_model

            logger.info(f"Created {len(models)} models from DataFrame")
            return models

        except Exception as e:
            logger.error(f"Error creating models from DataFrame: {e}")
            return {}

    @staticmethod
    def get_analytics_from_models(models: Dict[str, BaseModel]) -> Dict[str, Any]:
        """Extract analytics from all models"""
        analytics = {}

        try:
            if 'access' in models:
                access_data = models['access'].to_dict()
                analytics.update({
                    'total_events': access_data.get('total_events', 0),
                    'top_users': [
                        {'user_id': k, 'count': v} 
                        for k, v in sorted(
                            access_data.get('user_activity', {}).items(),
                            key=lambda x: x[1], reverse=True
                        )
                    ],
                    'top_doors': [
                        {'door_id': k, 'count': v}
                        for k, v in sorted(
                            access_data.get('door_activity', {}).items(),
                            key=lambda x: x[1], reverse=True
                        )
                    ],
                    'access_patterns': access_data.get('access_patterns', {})
                })

            if 'anomaly' in models:
                anomaly_model = models['anomaly']
                analytics['anomalies'] = {
                    'total_anomalies': len(anomaly_model.anomalies),
                    'anomaly_types': {}
                }

                # Count anomaly types
                for anomaly in anomaly_model.anomalies:
                    anomaly_type = anomaly.get('type', 'unknown')
                    analytics['anomalies']['anomaly_types'][anomaly_type] = (
                        analytics['anomalies']['anomaly_types'].get(anomaly_type, 0) + 1
                    )

            return analytics

        except Exception as e:
            logger.error(f"Error extracting analytics from models: {e}")
            return {}


# Export all classes and functions
__all__ = [
    'BaseModel',
    'AccessEventModel', 
    'AnomalyDetectionModel',
    'ModelFactory'
]
