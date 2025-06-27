import pytest
pytest.importorskip("pandas")
import pandas as pd
from services.analytics_computation import generate_basic_analytics, generate_sample_analytics
from services.analytics_ingestion import AnalyticsDataAccessor


def test_generate_basic_analytics():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "y"]})
    result = generate_basic_analytics(df)
    assert result["status"] == "success"
    assert result["total_rows"] == 3
    assert "a" in result["summary"]


def test_generate_sample_analytics():
    result = generate_sample_analytics()
    assert result["status"] == "success"
    assert result["total_rows"] > 0


def test_accessor_no_data(tmp_path):
    accessor = AnalyticsDataAccessor(base_data_path=str(tmp_path))
    df, meta = accessor.get_processed_database()
    assert df.empty
    assert meta == {}
