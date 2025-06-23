"""
Simple service tests
"""
import pandas as pd
from services.analytics_service import AnalyticsService


class TestAnalyticsService:
    """Test analytics service"""

    def setup_method(self) -> None:
        self.service = AnalyticsService()

    def test_analyze_empty_data(self) -> None:
        result = self.service.analyze_data(pd.DataFrame())
        assert not result.success
        assert "No data provided" in result.error

    def test_analyze_valid_data(self) -> None:
        data = pd.DataFrame({
            'person_id': ['EMP001', 'EMP002'],
            'door_id': ['DOOR001', 'DOOR002'],
            'access_result': ['Granted', 'Denied']
        })
        result = self.service.analyze_data(data)
        assert result.success
        assert result.data['total_records'] == 2
        assert result.data['unique_users'] == 2
