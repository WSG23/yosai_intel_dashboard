# yosai_intel_dashboard/components/weak_signal_panel.py

from dash import html
import dash_bootstrap_components as dbc
from flask_babel import _l


# Example signal card
def signal_card(prefix, code, severity, location, description, timestamp):
    severity_class = f"signal-{severity.lower()}"
    return dbc.Card(
        [
            dbc.CardHeader(
                _l("[{prefix}-{code}] - {severity}").format(
                    prefix=prefix, code=code, severity=severity
                ),
                className=f"signal-card-header {severity_class}",
            ),
            dbc.CardBody(
                [
                    html.P(_l("Location: {location}").format(location=location)),
                    html.P(
                        _l("Description: {description}").format(description=description)
                    ),
                    html.P(_l("Timestamp: {timestamp}").format(timestamp=timestamp)),
                ]
            ),
        ],
        className="signal-card",
    )


# Expandable category block
def category_block(title, signals, category_id):
    return html.Details(
        [
            html.Summary(
                _l("{title} ({count})").format(title=title, count=len(signals)),
                className="signal-summary",
            ),
            html.Div(signals, className="signal-category-content"),
        ],
        id=category_id,
        className="signal-category",
    )


layout = html.Div(
    [
        html.H4(_l("Weak-Signal Live Feed"), className="panel-header"),
        category_block(
            _l("News Scraping"),
            [
                signal_card(
                    "N",
                    "0001",
                    "High",
                    "Yokohama",
                    "Foreign actor probing energy facilities",
                    "25 June 2025",
                )
            ],
            "weak-signal-news",
        ),
        category_block(
            _l("Cross-Location"),
            [
                signal_card(
                    "CO",
                    "0001",
                    "Medium",
                    "Osaka HQ + Tokyo Base",
                    "Simultaneous badge denial",
                    "25 June 2025",
                )
            ],
            "weak-signal-cross-location",
        ),
        category_block(
            _l("Cross-Organization"),
            [
                signal_card(
                    "GS",
                    "0001",
                    "Low",
                    "3rd Party Vendor",
                    "Matching token IDs detected in external firm",
                    "25 June 2025",
                ),
                signal_card(
                    "GS",
                    "0002",
                    "Medium",
                    "Contractor Campus",
                    "Repeated denied access at midnight",
                    "25 June 2025",
                ),
            ],
            "weak-signal-cross-organization",
        ),
    ],
    className="weak-signal-panel",
)
