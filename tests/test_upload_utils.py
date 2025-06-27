import base64
import pytest

pd = pytest.importorskip("pandas")
from services.upload_utils import parse_uploaded_file


def _to_data_url(text: str, mime: str) -> str:
    encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def test_parse_csv_upload() -> None:
    csv = "a,b\n1,2\n3,4\n"
    contents = _to_data_url(csv, "text/csv")
    result = parse_uploaded_file(contents, "test.csv")
    assert result["success"] is True
    df = result["data"]
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_parse_json_upload() -> None:
    json_text = '[{"a":1,"b":2},{"a":3,"b":4}]'
    contents = _to_data_url(json_text, "application/json")
    result = parse_uploaded_file(contents, "data.json")
    assert result["success"] is True
    df = result["data"]
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 2


def test_invalid_upload() -> None:
    contents = "data:text/csv;base64,invalid"
    result = parse_uploaded_file(contents, "bad.csv")
    assert result["success"] is False
