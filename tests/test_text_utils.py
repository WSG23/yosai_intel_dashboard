"""
Tests for text utilities
"""
import pytest
from utils.text_utils import safe_text, format_file_size, truncate_text


def test_safe_text():
    """Test safe_text function"""
    assert safe_text("hello") == "hello"
    assert safe_text(123) == "123"
    assert safe_text(None) == ""
    assert safe_text("") == ""


def test_format_file_size():
    """Test file size formatting"""
    assert format_file_size(0) == "0 B"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1024 * 1024) == "1.0 MB"
    assert format_file_size(500) == "500 B"


def test_truncate_text():
    """Test text truncation"""
    assert truncate_text("hello", 10) == "hello"
    assert truncate_text("hello world", 5) == "he..."
    assert truncate_text("hello world", 11) == "hello world"


if __name__ == "__main__":
    pytest.main([__file__])
