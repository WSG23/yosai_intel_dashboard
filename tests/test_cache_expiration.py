import time
from services.analytics_service import AnalyticsService, AnalyticsConfig


def test_cache_expiration():
    config = AnalyticsConfig(cache_timeout_seconds=1)
    service = AnalyticsService(config)

    call_count = {"count": 0}

    def func():
        call_count["count"] += 1
        return call_count["count"]

    # First call caches the result
    assert service._get_cached_or_execute("test", func) == 1
    assert call_count["count"] == 1

    # Second call within timeout uses cache
    assert service._get_cached_or_execute("test", func) == 1
    assert call_count["count"] == 1

    # Wait for cache to expire
    time.sleep(1.1)

    # After expiration the function should run again
    assert service._get_cached_or_execute("test", func) == 2
    assert call_count["count"] == 2

