import pytest

# Skip tests if dash or pandas not installed
pytest.importorskip("dash")
pytest.importorskip("pandas")

import pandas as pd
from dash import Dash, html
import dash_bootstrap_components as dbc
from dash.testing.wait import until


class DummyStore:
    def __init__(self):
        self.files = {}

    def add_file(self, name, df):
        self.files[name] = df

    def get_filenames(self):
        return list(self.files.keys())

    def get_all_data(self):
        return self.files.copy()

    def clear_all(self):
        self.files.clear()


class DummyAnalyticsService:
    def get_analytics_by_source(self, src: str):
        return {
            "status": "success",
            "total_events": 10,
            "unique_users": 3,
            "success_rate": 0.8,
        }


# ----------------------------------------------------------------------
# File upload callback test
# ----------------------------------------------------------------------

def test_file_upload_callback_success(dash_duo, monkeypatch, tmp_path):
    import pages.file_upload as file_upload

    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    def mock_parse(contents, filename):
        return {"success": True, "data": df}

    def mock_preview(data, filename):
        return html.Div("preview", id="preview")

    def mock_update(filename, data, store):
        store.add_file(filename, data)
        return {
            "filename": filename,
            "rows": len(data),
            "columns": len(data.columns),
            "column_names": list(data.columns),
        }

    store = DummyStore()

    monkeypatch.setattr(file_upload, "parse_uploaded_file", mock_parse)
    monkeypatch.setattr(file_upload, "generate_preview", mock_preview)
    monkeypatch.setattr(file_upload, "update_upload_state", mock_update)
    monkeypatch.setattr(file_upload, "_uploaded_data_store", store)

    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
    app.layout = html.Div([file_upload.layout()])

    dash_duo.start_server(app)

    csv_path = tmp_path / "sample.csv"
    df.to_csv(csv_path, index=False)

    dash_duo.wait_for_element("input[type='file']").send_keys(str(csv_path))

    def check_success():
        return "Successfully uploaded" in dash_duo.find_element("#upload-results").text

    until(check_success, timeout=4)


# ----------------------------------------------------------------------
# Deep analytics callback test
# ----------------------------------------------------------------------

def test_deep_analytics_security_callback(dash_duo, monkeypatch):
    import pages.deep_analytics as da

    monkeypatch.setattr(da, "get_analytics_service_safe", lambda: DummyAnalyticsService())
    monkeypatch.setattr(da, "get_data_source_options_safe", lambda: [{"label": "Test", "value": "upload:test.csv"}])
    monkeypatch.setattr(da, "get_latest_uploaded_source_value", lambda: "upload:test.csv")

    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
    app.layout = html.Div([da.layout()])

    dash_duo.start_server(app)

    dash_duo.wait_for_element("#security-btn").click()

    def check_result():
        return "Security Results" in dash_duo.find_element("#analytics-display-area").text

    until(check_result, timeout=4)

