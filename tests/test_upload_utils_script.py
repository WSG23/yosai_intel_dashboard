#!/usr/bin/env python3
"""
Test script to validate the upload fix works correctly.
Run this after implementing the fixes.
"""

import sys
import os
import base64
import json
import pytest

pytest.importorskip("pandas")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_csv_upload():
    """Test CSV upload functionality."""
    from services.upload_utils import parse_uploaded_file

    csv_data = "name,age,city\nJohn,25,NYC\nJane,30,LA\nBob,35,Chicago"
    encoded_csv = base64.b64encode(csv_data.encode("utf-8")).decode("utf-8")
    test_contents = f"data:text/csv;base64,{encoded_csv}"

    result = parse_uploaded_file(test_contents, "test.csv")
    assert result["success"]
    df = result["data"]
    assert len(df) == 3
    assert list(df.columns) == ["name", "age", "city"]


def test_json_upload():
    """Test JSON upload functionality."""
    from services.upload_utils import parse_uploaded_file

    json_data = [
        {"name": "John", "age": 25, "city": "NYC"},
        {"name": "Jane", "age": 30, "city": "LA"},
        {"name": "Bob", "age": 35, "city": "Chicago"},
    ]
    json_string = json.dumps(json_data)
    encoded_json = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
    test_contents = f"data:application/json;base64,{encoded_json}"

    result = parse_uploaded_file(test_contents, "test.json")
    assert result["success"]
    df = result["data"]
    assert len(df) == 3
    assert list(df.columns) == ["name", "age", "city"]


def test_error_handling():
    """Test error handling for invalid files."""
    from services.upload_utils import parse_uploaded_file

    result = parse_uploaded_file("invalid_content", "test.csv")
    assert not result["success"]
    assert "error" in result


if __name__ == "__main__":
    all_passed = all(
        [
            test_csv_upload(),
            test_json_upload(),
            test_error_handling(),
        ]
    )
    if all_passed:
        print("🎉 ALL TESTS PASSED! Upload functionality is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")
