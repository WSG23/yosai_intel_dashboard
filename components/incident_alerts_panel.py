# yosai_intel_dashboard/components/incident_alerts_panel.py

from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc

# Categories and their properties
TICKET_CATEGORIES = [
    {"label": "Open Tickets", "color": "primary", "id": "ticket-open"},
    {"label": "Locked Tickets", "color": "secondary", "id": "ticket-locked"},
    {"label": "Resolved as Harmful", "color": "danger", "id": "ticket-resolved-harmful"},
    {"label": "Resolved as Tech. Malfunction", "color": "warning", "id": "ticket-resolved-malfunction"},
    {"label": "Resolved as Normal", "color": "success", "id": "ticket-resolved-normal"},
    {"label": "Dismissed Tickets", "color": "light", "id": "ticket-dismissed"},
]

# Sample ticket card layout
def ticket_card(ticket_id, threat_score, location, timestamp, area, device, group, result):
    return dbc.Card([
        dbc.CardHeader(f"Event ID: {ticket_id}", className="ticket-id"),
        dbc.CardBody([
            html.Div([
                html.Div("Threat Level:", className="ticket-threat-label"),
                dbc.Progress(value=threat_score, max=100, 
                             color=("success" if threat_score <= 40 else "warning" if threat_score <= 70 else "danger"),
                             striped=True, animated=True,
                             className="ticket-threat-potential")
            ]),
            html.Hr(),
            html.Div([
                html.P(f"Location: {location}"),
                html.P(f"Timestamp: {timestamp}"),
                html.P(f"Area: {area}"),
                html.P(f"Device: {device}"),
                html.P(f"Access Group: {group}"),
                html.P(f"Access Result: {result}")
            ])
        ])
    ], className="ticket-card")

# Category section with sample tickets
def ticket_category_block(cat):
    return dbc.AccordionItem([
        html.Div([
            ticket_card("C333333", 72, "Himeji Castle", "25 June 2025", "Server Room Door", "Server Room II", "IT Services", "Access"),
            ticket_card("D444444", 35, "Osaka HQ", "25 June 2025", "Main Entrance", "Door A", "General Staff", "Access Denied")
        ], className="ticket-list")
    ], title=f"{cat['label']} (2)", item_id=cat["id"])

layout = html.Div([
    html.H4("Incident Alerts", className="incident-panel-header"),
    dbc.Accordion(
        children=[ticket_category_block(cat) for cat in TICKET_CATEGORIES],
        start_collapsed=True,
        always_open=False,
        id="incident-alert-accordion"
    )
], className="incident-alert-panel")
