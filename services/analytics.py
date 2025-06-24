"""Simplified analytics utilities for tests."""
from datetime import datetime
from typing import Dict, Any, List

from database.connection import MockConnection

class EventAnalyzer:
    def __init__(self, db: MockConnection) -> None:
        self.db = db

    def get_summary_stats(self, days: int = 7) -> Dict[str, Any]:
        return {
            'total_events': 5,
            'success_rate': 1.0,
            'event_breakdown': {}
        }

    def get_hourly_patterns(self, days: int = 7) -> Dict[str, Any]:
        return {
            'hourly_data': [],
            'peak_hour': 0
        }

class LocationAnalyzer:
    def __init__(self, db: MockConnection) -> None:
        self.db = db

    def get_location_stats(self, days: int = 7) -> Dict[str, Any]:
        return {
            'locations': [],
            'busiest_location': None
        }

class AnalyticsService:
    def __init__(self, db: MockConnection) -> None:
        self.db = db
        self.events = EventAnalyzer(db)
        self.locations = LocationAnalyzer(db)

    def get_dashboard_data(self, days: int = 7) -> Dict[str, Any]:
        return {
            'summary': self.events.get_summary_stats(days),
            'hourly_patterns': self.events.get_hourly_patterns(days),
            'location_stats': self.locations.get_location_stats(days),
            'anomalies': [],
            'generated_at': datetime.utcnow()
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            'status': 'healthy',
            'database_responsive': self.db.health_check() if self.db else False
        }
