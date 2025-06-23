# models/base.py - Fixed type-safe version
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import pandas as pd
from datetime import datetime, timedelta
import logging

class BaseModel(ABC):
    """Base class for all data models with proper type safety"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    @abstractmethod
    def get_data(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Get data with optional filtering - subclasses must implement"""
        pass
    
    @abstractmethod
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics - subclasses must implement"""
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Basic data validation - can be overridden by subclasses"""
        if data is None or data.empty:
            return False
        return True

class AccessEventModel(BaseModel):
    """Model for access control events with proper type safety"""
    
    def get_data(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Get access events with optional filtering"""
        
        base_query = """
        SELECT 
            event_id,
            timestamp,
            person_id,
            door_id,
            badge_id,
            access_result,
            badge_status,
            door_held_open_time,
            entry_without_badge,
            device_status
        FROM access_events 
        WHERE 1=1
        """
        
        params = []
        
        # Use empty dict if filters is None to avoid type issues
        if filters is None:
            filters = {}
        
        if filters:
            if 'start_date' in filters:
                base_query += " AND timestamp >= %s"
                params.append(filters['start_date'])
            if 'end_date' in filters:
                base_query += " AND timestamp <= %s"
                params.append(filters['end_date'])
            if 'person_id' in filters:
                base_query += " AND person_id = %s"
                params.append(filters['person_id'])
            if 'door_id' in filters:
                base_query += " AND door_id = %s"
                params.append(filters['door_id'])
            if 'access_result' in filters:
                base_query += " AND access_result = %s"
                params.append(filters['access_result'])
        
        base_query += " ORDER BY timestamp DESC LIMIT 10000"
        
        try:
            df = self.db.execute_query(base_query, tuple(params) if params else None)
            return df if df is not None else pd.DataFrame()
        except Exception as e:
            logging.error(f"Error fetching access events: {e}")
            return pd.DataFrame()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        query = """
        SELECT 
            COUNT(*) as total_events,
            COUNT(DISTINCT person_id) as unique_people,
            COUNT(DISTINCT door_id) as unique_doors,
            SUM(CASE WHEN access_result = 'Granted' THEN 1 ELSE 0 END)::float / COUNT(*) as granted_rate,
            MIN(timestamp) as earliest_event,
            MAX(timestamp) as latest_event
        FROM access_events
        WHERE timestamp >= NOW() - INTERVAL '30 days'
        """
        
        try:
            result = self.db.execute_query(query)
            if result is not None and not result.empty:
                return result.iloc[0].to_dict()
            return {}
        except Exception as e:
            logging.error(f"Error getting summary stats: {e}")
            return {}
    
    def get_recent_events(self, hours: int = 24) -> pd.DataFrame:
        """Get recent events for dashboard"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return self.get_data({'start_date': cutoff_time})
    
    def get_trend_analysis(self, days: int = 30) -> pd.DataFrame:
        """Get trend analysis for analytics"""
        query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as total_events,
            SUM(CASE WHEN access_result = 'Granted' THEN 1 ELSE 0 END) as granted_events,
            COUNT(DISTINCT person_id) as unique_users
        FROM access_events 
        WHERE timestamp >= NOW() - INTERVAL '%s days'
        GROUP BY DATE(timestamp)
        ORDER BY date
        """
        
        try:
            result = self.db.execute_query(query, (days,))
            return result if result is not None else pd.DataFrame()
        except Exception as e:
            logging.error(f"Error getting trend analysis: {e}")
            return pd.DataFrame()

class AnomalyDetectionModel(BaseModel):
    """Model for anomaly detection data with proper type safety"""
    
    def get_data(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Get anomaly detections"""
        
        base_query = """
        SELECT 
            a.anomaly_id,
            a.event_id,
            a.anomaly_type,
            a.severity,
            a.confidence_score,
            a.description,
            a.detected_at,
            e.timestamp,
            e.person_id,
            e.door_id
        FROM anomaly_detections a
        JOIN access_events e ON a.event_id = e.event_id
        WHERE 1=1
        """
        
        params = []
        
        # Use empty dict if filters is None
        if filters is None:
            filters = {}
        
        if filters:
            if 'anomaly_type' in filters:
                base_query += " AND a.anomaly_type = %s"
                params.append(filters['anomaly_type'])
            if 'severity' in filters:
                base_query += " AND a.severity = %s"
                params.append(filters['severity'])
            if 'start_date' in filters:
                base_query += " AND a.detected_at >= %s"
                params.append(filters['start_date'])
        
        base_query += " ORDER BY a.detected_at DESC LIMIT 5000"
        
        try:
            result = self.db.execute_query(base_query, tuple(params) if params else None)
            return result if result is not None else pd.DataFrame()
        except Exception as e:
            logging.error(f"Error fetching anomalies: {e}")
            return pd.DataFrame()
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get anomaly summary statistics"""
        query = """
        SELECT 
            COUNT(*) as total_anomalies,
            AVG(confidence_score) as avg_confidence,
            COUNT(DISTINCT anomaly_type) as unique_types
        FROM anomaly_detections
        WHERE detected_at >= NOW() - INTERVAL '30 days'
        """
        
        try:
            result = self.db.execute_query(query)
            if result is not None and not result.empty:
                return result.iloc[0].to_dict()
            return {}
        except Exception as e:
            logging.error(f"Error getting anomaly stats: {e}")
            return {}
    
    def get_anomaly_breakdown(self) -> pd.DataFrame:
        """Get anomaly type breakdown for charts"""
        query = """
        SELECT 
            anomaly_type,
            COUNT(*) as count,
            AVG(confidence_score) as avg_confidence
        FROM anomaly_detections
        WHERE detected_at >= NOW() - INTERVAL '30 days'
        GROUP BY anomaly_type
        ORDER BY count DESC
        """
        
        try:
            result = self.db.execute_query(query)
            return result if result is not None else pd.DataFrame()
        except Exception as e:
            logging.error(f"Error getting anomaly breakdown: {e}")
            return pd.DataFrame()

# Factory class for creating model instances (modular and testable)
class ModelFactory:
    """Factory class for creating data model instances"""
    
    @staticmethod
    def create_access_model(db_connection) -> AccessEventModel:
        """Create an AccessEventModel instance"""
        return AccessEventModel(db_connection)
    
    @staticmethod
    def create_anomaly_model(db_connection) -> AnomalyDetectionModel:
        """Create an AnomalyDetectionModel instance"""
        return AnomalyDetectionModel(db_connection)
    
    @staticmethod
    def create_all_models(db_connection) -> Dict[str, BaseModel]:
        """Create all standard models with a single data source"""
        return {
            'access': ModelFactory.create_access_model(db_connection),
            'anomaly': ModelFactory.create_anomaly_model(db_connection)
        }

__all__ = ['BaseModel', 'AccessEventModel', 'AnomalyDetectionModel', 'ModelFactory']
