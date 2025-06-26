
# test_layout.py - Minimal working layout for testing
from dash import html, dcc
import dash_bootstrap_components as dbc

def test_layout():
    return dbc.Container([
        html.H1("🔍 Deep Analytics - Test", className="text-primary"),
        dbc.Alert("UI components working!", color="success"),
        dcc.Dropdown(
            options=[{"label": "Test", "value": "test"}],
            value="test"
        ),
        dbc.Button("Test Button", color="primary")
    ])
