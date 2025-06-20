"""
Tests for File Upload Plugin
"""
import pytest
import pandas as pd
from pages.file_upload import (
    _create_success_alert,
    _create_warning_alert,
    _create_error_alert,
    _create_file_info_card,
)


def test_file_upload_page_import():
    """Test that file upload page can be imported"""
    try:
        from pages.file_upload import layout, register_file_upload_callbacks
        assert layout is not None
        assert register_file_upload_callbacks is not None
    except ImportError:
        pytest.skip("File upload page components not available")


def test_alert_components():
    """Test alert component creation"""
    try:
        success_alert = _create_success_alert("Test success")
        warning_alert = _create_warning_alert("Test warning")
        error_alert = _create_error_alert("Test error")

        assert success_alert is not None
        assert warning_alert is not None
        assert error_alert is not None

    except ImportError:
        pytest.skip("Dash components not available for testing")


def test_file_info_card():
    """Test file info card creation"""
    try:
        test_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })

        info_card = _create_file_info_card(test_df, "test.csv")
        assert info_card is not None

    except ImportError:
        pytest.skip("Components not available for testing")


if __name__ == "__main__":
    pytest.main([__file__])
