# yosai_intel_dashboard/components/bottom_panel.py

from dash import html, dcc

layout = html.Div([
    html.Div([
        html.H4("Incident Detection Breakdown"),
        html.Div([
            html.Div([html.Div(label, className="chip gold") for label in [
                "Access Outcome", "Unusual Door", "Potential Tailgating", "Unusual Group"]], className="chip-row"),
            html.Div([html.Div(label, className="chip") for label in [
                "Unusual Path", "Unusual Time", "Multiple Attempts", "Location Criticality"]], className="chip-row"),
            html.Div([html.Div(label, className="chip gold") for label in [
                "Interaction Effects", "Token History", "Cross-Location", "Cross-Organization"]], className="chip-row"),
            html.Div("Tech. Malfunction", className="chip gray")
        ])
    ], className="bottom-column"),

    html.Div([
        html.H4("Respond"),
        html.Div("Action III", className="respond-label"),
        html.Div("Ticket I Action I", className="ticket-box"),
        html.Button("Mark As Completed", className="complete-button")
    ], className="bottom-column respond"),

    html.Div([
        html.H4("Resolve"),
        html.Div([
            html.Div([
                dcc.Checklist([
                    {"label": "Action I", "value": "A1"},
                    {"label": "Action II", "value": "A2"},
                    {"label": "Action III", "value": "A3"},
                    {"label": "Action IV", "value": "A4"},
                ], id="action-checklist", className="action-checklist")
            ]),
            html.Button("Resolve As Harmful", className="resolve-button"),
            html.Button("Resolve As Malfunction", className="resolve-button"),
            html.Button("Resolve As Normal", className="resolve-button"),
            html.Button("Dismiss", className="resolve-button")
        ])
    ], className="bottom-column")
], className="bottom-panel")
