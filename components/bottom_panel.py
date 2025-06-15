# yosai_intel_dashboard/components/bottom_panel.py

from dash import html, dcc
import dash_bootstrap_components as dbc

# Sample detection chips (can be dynamic later)
detection_chips = [
    {"label": "Access Outcome", "class": "detection-access-outcome", "score": 60},
    {"label": "Unusual Path", "class": "detection-unusual-path", "score": 80},
    {"label": "Unusual Time", "class": "detection-unusual-time", "score": 40},
    {"label": "Tech. Malfunction", "class": "detection-tech-malfunction", "score": 30}
]

# Render detection chips with a red-to-transparent gradient
def chip_element(chip):
    percent = chip["score"]
    bar_style = {
        "background": f"linear-gradient(to right, rgba(255, 0, 0, 0.7) {percent}%, rgba(255, 0, 0, 0) {percent}%)"
    }
    return html.Div(
        chip["label"],
        className=f"detection-chip {chip['class']}",
        style=bar_style
    )

layout = html.Div([
    html.Div([
        html.H5("Incident Detection Panel", className="panel-header"),
        html.Div([chip_element(c) for c in detection_chips], className="detection-chip-container")
    ], className="detection-breakdown"),

    html.Div([
        html.Div([
            html.Div("Selected Ticket ID: C333333", id="selected-ticket-id", className="ticket-id-label"),
            html.Hr(),
            dbc.Button("Mark as Complete", id="response-mark-complete-button", color="success", className="mb-2"),
            html.Div([
                dbc.Button("Action 1", id="response-action-1", color="primary", className="mx-1"),
                dbc.Button("Action 2", id="response-action-2", color="primary", className="mx-1"),
                dbc.Button("Action 3", id="response-action-3", color="primary", className="mx-1"),
                dbc.Button("Action 4", id="response-action-4", color="primary", className="mx-1"),
            ], id="response-sub-action-section", className="mb-2"),
            html.Hr(),
            html.Div([
                dbc.Button("Resolve as Harmful", id="response-resolve-harmful", color="danger", className="mx-1"),
                dbc.Button("Resolve as Malfunction", id="response-resolve-malfunction", color="warning", className="mx-1"),
                dbc.Button("Resolve as Normal", id="response-resolve-normal", color="success", className="mx-1"),
                dbc.Button("Dismiss", id="response-dismiss", color="secondary", className="mx-1"),
            ], id="resolve-incident-panel")
        ], className="response-panel")
    ])
], className="incident-detection-panel")

