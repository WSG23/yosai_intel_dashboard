import pandas as pd
from services.analytics import AnalyticsService


def test_summary_stats_basic() -> None:
    df = pd.DataFrame({
        "person_id": ["A", "B"],
        "door_id": ["D1", "D2"],
        "access_result": ["Granted", "Denied"],
        "timestamp": pd.date_range("2024-01-01", periods=2, freq="H"),
    })
    service = AnalyticsService(None)
    stats = service.get_summary_stats(df)
    assert stats["total_events"] == 2
    assert stats["unique_persons"] == 2
    assert stats["unique_doors"] == 2


def test_detect_anomalies_hours() -> None:
    df = pd.DataFrame({"timestamp": pd.to_datetime(["2024-01-01 01:00", "2024-01-01 10:00"])})
    service = AnalyticsService(None)
    result = service.detect_anomalies(df)
    assert len(result) == 1
