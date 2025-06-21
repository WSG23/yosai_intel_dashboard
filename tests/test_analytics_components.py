import base64
import json
from datetime import datetime, timedelta

import pandas as pd

from components.analytics import (
    FileProcessor,
    AnalyticsGenerator,
    create_dual_file_uploader,
    create_data_preview,
    create_analytics_charts,
    create_summary_cards,
)


def test_file_processing() -> None:
    """Ensure FileProcessor handles CSV input correctly."""
    sample_data = pd.DataFrame(
        {
            "person_id": ["EMP001", "EMP002", "EMP001", "EMP003"],
            "door_id": ["MAIN_ENTRANCE", "SERVER_ROOM", "MAIN_ENTRANCE", "LAB_A"],
            "access_result": ["Granted", "Denied", "Granted", "Granted"],
            "timestamp": [datetime.now() - timedelta(hours=i) for i in range(4)],
        }
    )
    csv_content = sample_data.to_csv(index=False)
    encoded = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    contents = f"data:text/csv;base64,{encoded}"

    result = FileProcessor.process_file_content(contents, "test.csv")
    assert result is not None and len(result) == 4

    valid, message, _ = FileProcessor.validate_dataframe(sample_data)
    assert valid, message

    assert FileProcessor.process_file_content("", "test.csv") is None
    assert FileProcessor.process_file_content("invalid_content", "test.csv") is None
    assert (
        FileProcessor.process_file_content("data:text/csvnocommahere", "test.csv")
        is None
    )


def test_analytics_generation() -> None:
    """Validate analytics generation from a small DataFrame."""
    sample_data = pd.DataFrame(
        {
            "person_id": ["EMP001", "EMP002", "EMP001", "EMP003", "EMP001"],
            "door_id": ["MAIN", "SERVER", "MAIN", "LAB", "SERVER"],
            "access_result": ["Granted", "Denied", "Granted", "Granted", "Granted"],
            "timestamp": [
                datetime(2025, 1, 1, 9, 0),
                datetime(2025, 1, 1, 14, 30),
                datetime(2025, 1, 1, 17, 45),
                datetime(2025, 1, 2, 8, 15),
                datetime(2025, 1, 2, 10, 30),
            ],
        }
    )

    analytics = AnalyticsGenerator.generate_analytics(sample_data)
    assert analytics.get("total_events") == 5
    assert "Granted" in analytics.get("access_patterns", {})
    assert "EMP001" in analytics.get("top_users", {})

    empty_analytics = AnalyticsGenerator.generate_analytics(pd.DataFrame())
    assert empty_analytics == {}


def test_component_creation() -> None:
    """Verify dashboard component factory helpers."""
    uploader = create_dual_file_uploader()
    assert uploader is not None

    sample_data = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})

    preview = create_data_preview(sample_data, "test.csv")
    assert preview is not None

    preview_none = create_data_preview(None, "")
    assert preview_none is not None

    analytics_data = {
        "access_patterns": {"Granted": 80, "Denied": 20},
        "hourly_patterns": {"9": 10, "14": 15, "17": 8},
        "top_users": {"EMP001": 25, "EMP002": 20},
        "top_doors": {"MAIN": 30, "SERVER": 15},
    }

    charts = create_analytics_charts(analytics_data)
    assert charts is not None

    charts_empty = create_analytics_charts({})
    assert charts_empty is not None

    cards = create_summary_cards(analytics_data)
    assert cards is not None

    cards_empty = create_summary_cards({})
    assert cards_empty is not None


def test_type_safety() -> None:
    """Check handling of invalid inputs and None values."""
    invalid_cases = [
        ("", "test.csv"),
        ("invalid", "test.csv"),
        ("data:", "test.csv"),
        ("data:text/csv", "test.csv"),
        ("data:text/csv;base64,", "test.csv"),
        ("data:text/csv;base64,invalid!", "test.csv"),
    ]
    for contents, filename in invalid_cases:
        assert FileProcessor.process_file_content(contents, filename) is None

    analytics_none = AnalyticsGenerator.generate_analytics(None)
    assert analytics_none == {}

    valid, message, _ = FileProcessor.validate_dataframe(None)
    assert not valid and "No data provided" in message

    empty_df = pd.DataFrame()
    valid, message, _ = FileProcessor.validate_dataframe(empty_df)
    assert not valid and "empty" in message.lower()


def test_integration() -> None:
    """Run a small end-to-end pipeline."""
    from components.analytics import create_data_preview

    test_data = pd.DataFrame(
        {
            "employee_id": ["E001", "E002", "E001"],
            "access_point": ["ENTRANCE", "SERVER", "ENTRANCE"],
            "result": ["GRANTED", "DENIED", "GRANTED"],
            "event_datetime": [
                "2025-01-01 09:00:00",
                "2025-01-01 14:30:00",
                "2025-01-01 17:45:00",
            ],
        }
    )

    valid, message, _ = FileProcessor.validate_dataframe(test_data)
    assert valid, message

    analytics = AnalyticsGenerator.generate_analytics(test_data)
    assert analytics.get("total_events") == 3

    preview = create_data_preview(test_data, "integration_test.csv")
    assert preview is not None

    csv_content = test_data.to_csv(index=False)
    encoded = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")
    contents = f"data:text/csv;base64,{encoded}"
    processed_df = FileProcessor.process_file_content(contents, "integration_test.csv")
    assert processed_df is not None and len(processed_df) == 3


def test_json_processing() -> None:
    """Ensure JSON uploads are parsed properly."""
    test_data = [
        {"person_id": "EMP001", "door_id": "MAIN", "access_result": "Granted"},
        {"person_id": "EMP002", "door_id": "SERVER", "access_result": "Denied"},
    ]

    json_content = json.dumps(test_data)
    encoded = base64.b64encode(json_content.encode("utf-8")).decode("utf-8")
    contents = f"data:application/json;base64,{encoded}"

    result = FileProcessor.process_file_content(contents, "test.json")
    assert result is not None and len(result) == 2

    dict_data = {"data": test_data}
    json_content = json.dumps(dict_data)
    encoded = base64.b64encode(json_content.encode("utf-8")).decode("utf-8")
    contents = f"data:application/json;base64,{encoded}"

    result = FileProcessor.process_file_content(contents, "test_dict.json")
    assert result is not None and len(result) == 2
