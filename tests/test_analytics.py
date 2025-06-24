"""Analytics service tests"""
import pytest
from services.analytics import EventAnalyzer, LocationAnalyzer, AnalyticsService
from database.connection import MockConnection

class TestAnalyticsService:
    def test_event_analyzer_summary_stats(self, mock_db):
        analyzer = EventAnalyzer(mock_db)
        stats = analyzer.get_summary_stats(days=7)
        assert 'total_events' in stats
        assert 'success_rate' in stats
        assert 'event_breakdown' in stats
        assert isinstance(stats['total_events'], int)
        assert isinstance(stats['success_rate'], float)

    def test_event_analyzer_hourly_patterns(self, mock_db):
        analyzer = EventAnalyzer(mock_db)
        patterns = analyzer.get_hourly_patterns(days=7)
        assert 'hourly_data' in patterns
        assert 'peak_hour' in patterns
        assert isinstance(patterns['hourly_data'], list)

    def test_location_analyzer_stats(self, mock_db):
        analyzer = LocationAnalyzer(mock_db)
        stats = analyzer.get_location_stats(days=7)
        assert 'locations' in stats
        assert 'busiest_location' in stats
        assert isinstance(stats['locations'], list)

    def test_analytics_service_dashboard_data(self, analytics_service):
        data = analytics_service.get_dashboard_data(days=7)
        required_keys = ['summary', 'hourly_patterns', 'location_stats', 'anomalies', 'generated_at']
        for key in required_keys:
            assert key in data

    def test_analytics_service_health_check(self, analytics_service):
        health = analytics_service.health_check()
        assert 'status' in health
        assert 'database_responsive' in health
        assert health['status'] in ['healthy', 'unhealthy']
