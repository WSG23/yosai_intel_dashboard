"""Integration tests"""
class TestIntegration:
    def test_full_system_integration(self, test_container):
        config = test_container.get('config')
        db_connection = test_container.get('database_connection')
        analytics_service = test_container.get('analytics_service')
        assert config.app.environment == "test"
        assert db_connection.health_check() is True
        dashboard_data = analytics_service.get_dashboard_data()
        assert 'summary' in dashboard_data
        assert 'generated_at' in dashboard_data

    def test_error_propagation(self, test_container):
        analytics_service = test_container.get('analytics_service')
        health = analytics_service.health_check()
        assert 'status' in health
