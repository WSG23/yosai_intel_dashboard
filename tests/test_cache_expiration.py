import time
import pytest
pytest.skip("legacy test", allow_module_level=True)
from services.analytics import AnalyticsService


def test_cache_expiration():
    service = AnalyticsService(None)

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

