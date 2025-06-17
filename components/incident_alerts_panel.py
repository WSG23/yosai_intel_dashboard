# yosai_intel_dashboard/components/incident_alerts_panel.py

from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from flask_babel import _l

# Categories and their properties
TICKET_CATEGORIES = [
    {"label": _l("Open Tickets"), "color": "primary", "id": "ticket-open"},
    {"label": _l("Locked Tickets"), "color": "secondary", "id": "ticket-locked"},
    {
        "label": _l("Resolved as Harmful"),
        "color": "danger",
        "id": "ticket-resolved-harmful",
    },
    {
        "label": _l("Resolved as Tech. Malfunction"),
        "color": "warning",
        "id": "ticket-resolved-malfunction",
    },
    {
        "label": _l("Resolved as Normal"),
        "color": "success",
        "id": "ticket-resolved-normal",
    },
    {"label": _l("Dismissed Tickets"), "color": "light", "id": "ticket-dismissed"},
]


# Sample ticket card layout
def ticket_card(
    ticket_id, threat_score, location, timestamp, area, device, group, result
):
    return dbc.Card(
        [
            dbc.CardHeader(f"Event ID: {ticket_id}", className="ticket-id"),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.Div(
                                _l("Threat Level:"), className="ticket-threat-label"
                            ),
                            dbc.Progress(
                                value=threat_score,
                                max=100,
                                color=(
                                    "success"
                                    if threat_score <= 40
                                    else "warning" if threat_score <= 70 else "danger"
                                ),
                                striped=True,
                                animated=True,
                                className="ticket-threat-potential",
                            ),
                        ]
                    ),
                    html.Hr(),
                    html.Div(
                        [
                            html.P(
                                _l("Location: {location}").format(location=location)
                            ),
                            html.P(
                                _l("Timestamp: {timestamp}").format(timestamp=timestamp)
                            ),
                            html.P(_l("Area: {area}").format(area=area)),
                            html.P(_l("Device: {device}").format(device=device)),
                            html.P(_l("Access Group: {group}").format(group=group)),
                            html.P(_l("Access Result: {result}").format(result=result)),
                        ]
                    ),
                ]
            ),
        ],
        className="ticket-card",
    )


# Category section with sample tickets
def ticket_category_block(cat):
    return dbc.AccordionItem(
        [
            html.Div(
                [
                    ticket_card(
                        "C333333",
                        72,
                        "Himeji Castle",
                        "25 June 2025",
                        "Server Room Door",
                        "Server Room II",
                        "IT Services",
                        "Access",
                    ),
                    ticket_card(
                        "D444444",
                        35,
                        "Osaka HQ",
                        "25 June 2025",
                        "Main Entrance",
                        "Door A",
                        "General Staff",
                        "Access Denied",
                    ),
                ],
                className="ticket-list",
            )
        ],
        title=f"{cat['label']} (2)",
        item_id=cat["id"],
    )


layout = html.Div(
    [
        html.H4(_l("Incident Alerts"), className="incident-panel-header"),
        dbc.Accordion(
            children=[ticket_category_block(cat) for cat in TICKET_CATEGORIES],
            start_collapsed=True,
            always_open=False,
            id="incident-alert-accordion",
        ),
    ],
    className="incident-alert-panel",
)
