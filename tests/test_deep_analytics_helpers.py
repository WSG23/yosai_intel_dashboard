import pandas as pd
from pages import deep_analytics


def test_validate_file_returns_types() -> None:
    df = pd.DataFrame({'A': [1, 2]})
    valid, alerts, suggestions = deep_analytics._validate_file(deep_analytics.FileProcessor, df, 'file.csv')
    assert isinstance(valid, bool)
    assert isinstance(alerts, list)
    assert isinstance(suggestions, list)


def test_generate_analytics_data_returns_dict() -> None:
    df = pd.DataFrame({'A': [1, 2]})
    analytics = deep_analytics._generate_analytics_data(None, df, 1)
    assert isinstance(analytics, dict)
